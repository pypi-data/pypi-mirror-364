import requests
import base64
import hashlib
import random
import json
import subprocess
import time
from send2trash import send2trash
import os
import argparse
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

class Whitedot:
    def create_keys(self):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        priv = key.private_bytes(
            serialization.Encoding.DER,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        )
        pub = key.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo
        )
        priv = base64.b64encode(priv).decode()
        pub = base64.b64encode(pub).decode()
        return str(priv), str(pub)
    def join_network(self, public_key):
        url = "https://whitedot.pythonanywhere.com/join/"
        data = {
            "public_key": public_key,
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return "Success: " + response.text, 200
        else:
            return "Error: " + response.text, 400
    def submit_block(self, index, previous_hash, transaction, private_key, public_key):
        url = "https://whitedot.pythonanywhere.com/submit_block"
        nonce = 0
        timestamp = int(time.time())

        private_key_bytes = base64.b64decode(private_key)
        priv_key_obj = serialization.load_der_private_key(private_key_bytes, password=None, backend=default_backend())
        message = f"{index}-{previous_hash}-{transaction}-{timestamp}".encode()
        signature_bytes = priv_key_obj.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        signature = base64.b64encode(signature_bytes).decode()

        while True:
            nonce = nonce + 1
            block = {
            "index": str(index),
            "timestamp": str(int(timestamp)),
            "previous_hash": str(previous_hash),
            "transaction": str(transaction),
            "nonce": str(nonce),
            "signature": str(signature),
            "public_key": str(public_key)
            }
            blockjson = json.dumps(block, sort_keys=True)
            hash_object = hashlib.sha256(blockjson.encode())
            hash_hex = str(hash_object.hexdigest())
            if hash_hex.startswith("00000"):
                break
        data = {
            "index": str(index),
            "timestamp": str(int(timestamp)),
            "previous_hash": str(previous_hash),
            "transaction": str(transaction),
            "nonce": str(nonce),
            "signature": str(signature),
            "public_key": str(public_key)
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return "Success: " + response.text, 200
        else:
            return "Error: " + response.text, 400
    def vote_block(self, vote, index, private_key, public_key):
        url = "https://whitedot.pythonanywhere.com/vote/"
        private_key_bytes = base64.b64decode(private_key)
        private_key = serialization.load_der_private_key(private_key_bytes, password=None, backend=default_backend())
        message = f"{index}-{vote}".encode()
        signature_to_encode = private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        signature = base64.b64encode(signature_to_encode).decode()
        data = {
            "vote": vote,
            "index": index,
            "signature": signature,
            "public_key": public_key
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return "Success: " + response.text
        else:
            return "Error: " + response.text
    def get_blockchain(self):
        response = requests.get("https://whitedot.pythonanywhere.com/blockchain/")
        if response.status_code == 200:
            return response.text
        else:
            return "Error: " + response.text
    def get_mempool(self):
        response = requests.get("https://whitedot.pythonanywhere.com/mempool/")
        if response.status_code == 200:
            return response.text
        else:
            return "Error: " + response.text
    def verify_blockchain(self, blockchain):
        blockchain = json.loads(str(blockchain))

        verified = 1
        reasons = []
        users = {}
        
        for i in range(len(blockchain)):
            block = blockchain[i]
            public_key = block["public_key"]
            signature = block["signature"]
            if i == 0 and block["transaction"] == "Genesis Block" and block["previous_hash"] == "0":
                previous_hash = hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
                previous_timestamp = 0
                pass
            else:
                if previous_hash == block["previous_hash"]:
                    pass
                else:
                    verified = 0
                    reasons.append("Invalid previous_hash")

                if hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest().startswith("00000"):
                    pass
                else:
                    verified = 0
                    reasons.append("Not enough hash zeros")
                message = f"{block['index']}-{block['previous_hash']}-{block['transaction']}-{block['timestamp']}"
                public_key_obj = serialization.load_der_public_key(base64.b64decode(public_key), backend=default_backend())
                try:
                    public_key_obj.verify(
                    base64.b64decode(block["signature"]),
                    message.encode(),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                    )
                except:
                    verified = 0
                    reasons.append("Invalid signature format.")

                # blocks have to be validated within one day or they are invalid.
                if int(previous_timestamp) < int(block["timestamp"]):
                    if int(block["timestamp"]) <= (time.time() + 120):
                        pass
                    else:
                        verified = 0
                        reasons.append("Timestamp is invalid. It is too far ahead.")
                else:
                    verified = 0
                    reasons.append("Timestamp is invalid. It is not increasing.")

                if not str(block["public_key"]) == str(str(block["transaction"]).split(" ")[0]):
                    verified = 0
                    reasons.append("Invalid public_key or sender field in transaction.")
                # sender amount recipient
                if not str(block["transaction"]).split(" ")[0] in users:
                    # if the block is within the time range, it recieves 10 bonus whitedots
                    if int(block["timestamp"]) <= 1760625480:
                        users[str(block["transaction"]).split(" ")[0]] = 10
                    else:
                        users[str(block["transaction"]).split(" ")[0]] = 0

                if not str(block["transaction"]).split(" ")[2] in users:
                    # if the block is within the time range, it recieves 10 bonus whitedots
                    if int(block["timestamp"]) <= 1760625480:
                        users[str(block["transaction"]).split(" ")[2]] = 10
                    else:
                        users[str(block["transaction"]).split(" ")[2]] = 0
                sender = str(block["transaction"]).split(" ")[0]
                amount = str(block["transaction"]).split(" ")[1]
                if not (str(amount).isdigit() and int(amount) > 0):
                    verified = 0
                    reasons.append("Amount is invalid.")
                else:
                    amount = int(amount)
                
                recipient = str(str(block["transaction"]).split(" ")[2])

                if not int(users[sender]) >= amount:
                    verified = 0
                    reasons.append("Amount is too much.")

                users[sender] = int(users[sender]) - amount
                users[recipient] = int(users[recipient]) + amount
                
                previous_hash = hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()
                previous_timestamp = block["timestamp"]

        if verified == 1:
            return "Blockchain is valid.", users, "Since blockchain is valid, reasons do not need to be shown."
        else:
            return "Blockchain is not valid", "Invalid balances cannot be shown.", reasons
dot = Whitedot()
def main():
    try:
        blockchain_verification = requests.get("https://whitedot.pythonanywhere.com/blockchain").text
        if dot.verify_blockchain(blockchain_verification)[0] == "Blockchain is valid.":
            parser = argparse.ArgumentParser(description="Whitedot Cryptocurrency")
            parser.add_argument('command', choices=["transfer", "listen", "create_keys", "get_balance", "info"], help='Command to run', nargs='?',default='info')
            args = parser.parse_args()
            blockchain_file = os.path.join("whitedot-cryptocurrency-authenticity", "blockchain.json")
            if os.path.exists(blockchain_file):
                try:
                    with open(blockchain_file, 'r', encoding='utf-8') as f:
                        local_chain_obj = json.load(f)
                except Exception as e:
                    print(f"Error loading blockchain file: {e}")
                server_chain_obj = json.loads(blockchain_verification)
                if server_chain_obj[:len(local_chain_obj)] != local_chain_obj:
                    print("The blockchain is not valid. It may have beeen tampered with, or there may have been an accident. Please contact contact@seafoodstudios.com to make sure the blockchain can be recovered. If this person is not cooperating, consider working with your community to create a new server from Whitedot's source code and a safer version of the blockchain.")
                    exit()
                
            if str(input("Would you like to download the blockchain and repository into the current directory? This is to ensure the central server cannot cheat, and contributes to the community. After this prompt, you will proceed to the process you chose (y/n): ")) == "y":
                print("Loading, currently downloading the repository of the cryptocurrency and the blockchain in the current directory to ensure that the server can't cheat.")
                repo_url = "https://github.com/SeafoodStudios/Whitedot"
                clone_dir = os.path.join("whitedot-cryptocurrency-authenticity", "repository")
                overridechoice = "undefined"
                if os.path.exists(clone_dir):
                    overridechoice = str(input("There seems to already be a folder named 'whitedot-cryptocurrency-authenticity', would you like to overwrite it? It is likely an old folder that this program made, but you are still strongly advised to check it if you think you created the file or another program did this (y/n): "))
                else:
                    try:
                        subprocess.run(["git", "clone", repo_url, clone_dir], check=True)
                        print("Repository downloaded.")
                        response = requests.get("https://whitedot.pythonanywhere.com/blockchain/")
                        if response.status_code == 200:
                            try:
                                with open(os.path.join("whitedot-cryptocurrency-authenticity", "blockchain.json"), "w", encoding="utf-8") as f:
                                    f.write(response.text)
                                print("Blockchain successfully downloaded.")
                                print("Now proceeding to the process you chose.")
                            except Exception as e:
                                print("Blockchain could not be downloaded.")
                                print(str(e))
                                print("Now proceeding to the process you chose.")
                        else:
                            print("Blockchain could not be fetched.")
                            print("Now proceeding to the process you chose.")
                    except Exception as e:
                        print(f"Error, repository could not be cloned. {e}")
                        print("Now proceeding to the process you chose.")
                if overridechoice == "y":
                    if os.path.exists(clone_dir):
                        send2trash(clone_dir)
                        try:
                            subprocess.run(["git", "clone", repo_url, clone_dir], check=True)
                            print("Repository downloaded.")
                            response = requests.get("https://whitedot.pythonanywhere.com/blockchain/")
                            if response.status_code == 200:
                                try:
                                    with open(os.path.join("whitedot-cryptocurrency-authenticity", "blockchain.json"), "w", encoding="utf-8") as f:
                                        f.write(response.text)
                                    print("Blockchain successfully downloaded.")
                                    print("Now proceeding to the process you chose.")
                                except Exception as e:
                                    print("Blockchain could not be downloaded.")
                                    print(str(e))
                                    print("Now proceeding to the process you chose.")
                            else:
                                print("Blockchain could not be fetched.")
                                print("Now proceeding to the process you chose.")
                        except Exception as e:
                            print(f"Error, repository could not be cloned. {e}")
                            print("Now proceeding to the process you chose.")
                    else:
                        print("This directory seems to have been changed mid-process, please try again.")
                        print("Now proceeding to the process you chose.")
                else:
                    print("You have chosen not to override the folder.")
                    print("Now proceeding to the process you chose.")
            else:
                print("You have chosen not to download the blockchain or repository into the currency directory. Now continuing to the process you chose.")
            if args.command == 'transfer':
                try:
                    print("\nWhitedot Transfer\nPlease note that after the transaction has been confirmed, it cannot be canceled. Your transaction may take some time, depending on how activate the network is for the results to be added to the blockchain.\nYou may cancel this command before you confirm by typing Control + C.\n")
                    
                    public_key = input("Enter your public key: ")
                    
                    private_key = input("Enter your private keys path: ")
                    with open(private_key, "rb") as f:
                        private_key_bytes = f.read()
                    private_key = base64.b64encode(private_key_bytes).decode()
                    
                    recipient = input("Enter the public key of your recipient: ")
                    amount = "unconfirmed"
                    while not amount.isdigit():
                        amount = input("Enter the amount you would like to send: ")

                    confirmation = "unconfirmed"
                    while not (confirmation == "y" or confirmation == "n"):
                        confirmation = input(f"Are you sure you would like to send this user {amount} Whitedots (y/n): ")

                    if confirmation == "y":
                        print("You chose to continue.")
                    else:
                        print("you chose to cancel.")
                        exit()
                    try:
                        blockchain_data = requests.get("https://whitedot.pythonanywhere.com/blockchain").text
                        if str(dot.verify_blockchain(blockchain_data)[0]) == "Blockchain is valid.":
                            blockchain_dict = json.loads(blockchain_data)
                            last_block = blockchain_dict[-1]
                            index = str(int(last_block["index"]) + 1)
                            block_json = json.dumps(blockchain_dict[-1], sort_keys=True).encode('utf-8')
                            hash_hex = hashlib.sha256(block_json).hexdigest()
                            result = dot.submit_block(index, hash_hex, f"{public_key} {amount} {recipient}", private_key, public_key)
                            if result[1] == 200:
                                print("Transaction complete!")
                            else:
                                print(f"An error occurred! Error: {result[0]}")
                        else:
                            exit()
                        
                    except Exception as e:
                        print(f"An error occured because of the given inputs, or the blockchain is invalid. Error: {e}")
                        exit()
                except Exception as e:
                    print(f"\nTransaction canceled due to user interference or errors. Error: {e}")
            elif args.command == 'create_keys':
                print("Key Creator")
                print("Make sure to save your keys once you created them! They cannot be recovered if you lose them!\n")
                try:
                    if os.path.exists("private_key.der"):
                        print("It seems you already have a private key saved.")
                        if input("Would you like to override it (y/n): ") == "y":
                            send2trash("private_key.der")
                        else:
                            print("Aborting...")
                            exit()
                    keys = dot.create_keys()
                    der_bytes = base64.b64decode(keys[0])
                    with open("private_key.der", "wb") as f:
                        f.write(der_bytes)
                    network = dot.join_network(keys[1])
                    if network[1] == 200:
                        pass
                    else:
                        print("Network error.")
                        exit()
                    print("Saved private key as private_key.der")
                    print(f"Saved public key as {keys[1]}")
                    print("You will have to wait 1-2 days before your key will be accepted.")
                except Exception as e:
                    print(f"Error: {e}")
            elif args.command == 'get_balance':
                print("Balance Finder")
                print("Loading...\n")
                get_blockchain = requests.get("https://whitedot.pythonanywhere.com/blockchain")
                if get_blockchain.status_code == 200:
                    user_balances = dot.verify_blockchain(get_blockchain.text)
                    if user_balances[0] == "Blockchain is not valid":
                        print("Blockchain is not valid. \n Aborting...")
                        exit()
                    py_user_balances = user_balances[1]
                    try:
                        while True:
                            user = input("Pick a user (enter their public key) to find their balance. Type Control + C to break out of this state: ")
                            if user in py_user_balances:
                                print("This user has " + str(py_user_balances[user]) + " Whitedots.")
                            else:
                                print("This user does not exist.")

                    except:
                        print("\nAn error occurred or the user decided to stop the program.")
                        exit()
                else:
                    print("Error, blockchain could not be fetched.")
            elif args.command == 'listen':
                print("Node Listener\n")
                listen_pub_key = str(input("Enter your public key: "))
                listen_priv_key = str(input("Enter your private key's path: "))
                with open(listen_priv_key, "rb") as f:
                    listen_private_key_bytes = f.read()
                listen_priv_key = base64.b64encode(listen_private_key_bytes).decode()
                print("\nNode is now listening for votes. Press Control + C to exit.\n")
                voted = []
                while True:
                    try:
                        mempool_json = requests.get("https://whitedot.pythonanywhere.com/mempool").text
                        mempool_dict = json.loads(mempool_json)
                        if not mempool_dict:
                            print("Mempool is empty.")
                        else:
                            blockchain_json = requests.get("https://whitedot.pythonanywhere.com/blockchain").text
                            block_hash = str(hashlib.sha256(str(mempool_dict[0]).encode()).hexdigest())
                            if block_hash in voted:
                                print("Passed block, block already voted on.")
                            else:
                                voted.append(block_hash)
                                blockchain_dict = json.loads(blockchain_json)
                                blockchain_dict.append(mempool_dict[0])
                                blockchain = json.dumps(blockchain_dict)
                                verify = dot.verify_blockchain(blockchain)
                                if str(verify[0]) == "Blockchain is valid.":
                                    private_key_bytes = base64.b64decode(listen_priv_key)
                                    private_key = serialization.load_der_private_key(private_key_bytes, password=None, backend=default_backend())

                                    message = f"""{mempool_dict[0]["index"]}-yes""".encode()
                                    signature_bytes = private_key.sign(
                                        message,
                                        padding.PKCS1v15(),
                                        hashes.SHA256()
                                    )
                                    signature_b64 = base64.b64encode(signature_bytes).decode()
                                    data = {
                                        "vote": "yes",
                                        "index": mempool_dict[0]["index"],
                                        "signature": signature_b64,
                                        "public_key": listen_pub_key
                                    }
                                    response = requests.post("https://whitedot.pythonanywhere.com/vote/", json=data)

                                    print(mempool_dict[0])
                                    print("Voted for block.")
                                else:
                                    private_key_bytes = base64.b64decode(listen_priv_key)
                                    private_key = serialization.load_der_private_key(private_key_bytes, password=None, backend=default_backend())

                                    message = f"""{mempool_dict[0]["index"]}-no""".encode()
                                    signature_bytes = private_key.sign(
                                        message,
                                        padding.PKCS1v15(),
                                        hashes.SHA256()
                                    )
                                    signature_b64 = base64.b64encode(signature_bytes).decode()
                                    data = {
                                        "vote": "no",
                                        "index": mempool_dict[0]["index"],
                                        "signature": signature_b64,
                                        "public_key": listen_pub_key
                                    }
                                    response = requests.post("https://whitedot.pythonanywhere.com/vote/", json=data)

                                    print(mempool_dict[0])
                                    print("Block invalid, block rejected.")
                    except Exception as e:
                        private_key_bytes = base64.b64decode(listen_priv_key)
                        private_key = serialization.load_der_private_key(private_key_bytes, password=None, backend=default_backend())

                        message = f"""{mempool_dict[0]["index"]}-no""".encode()
                        signature_bytes = private_key.sign(
                            message,
                            padding.PKCS1v15(),
                            hashes.SHA256()
                        )
                        signature_b64 = base64.b64encode(signature_bytes).decode()
                        data = {
                            "vote": "no",
                            "index": mempool_dict[0]["index"],
                            "signature": signature_b64,
                            "public_key": listen_pub_key
                        }
                        response = requests.post("https://whitedot.pythonanywhere.com/vote/", json=data)

                        print(mempool_dict[0])
                        print("Block invalid, block rejected.")
                    time.sleep(20)
            elif args.command == 'info':
                print("Whitedot Cryptocurrency Node")
                print("By SeafoodStudios")
                print("https://seafoodstudios.com\n")
                print("Commands:")
                print("whitedot transfer - This command allows you to transfer Whitedots with your account.")
                print("whitedot listen - This command listens for any new transactions to be voted for. It is very encouraged you run this repeatedly to contribute to the community.")
                print("whitedot create_keys - This command create your keys. Your public key is like your 'username' and your private key is like your 'password'. It then submits it to the server to be verified. You keys should be verified in around 1-2 days.")
                print("whitedot get_balance - This command gets the balance, based on the public key you provide.")
                print("whitedot info - This command gives information about the commands, precisely what you are doing. You can also run 'whitedot' to do the same thing.")
                print("\nThanks for using Whitedot, and please contribute to the community!")   
            else:
                print("Error: Invalid Command")
        else:
            print("The blockchain is not valid. It may have beeen tampered with, or there may have been an accident. Please contact contact@seafoodstudios.com to make sure the blockchain can be recovered. If this person is not cooperating, consider working with your community to create a new server from Whitedot's source code and a safer version of the blockchain.")
    except Exception as e:
        print(f"Process stopped due to user interference or errors. Error: {e}")
if __name__ == "__main__" :
    main()
