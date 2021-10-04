import json
import os
from web3 import Web3
from solcx import compile_standard, install_solc
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

    print("Installing...")
    install_solc("0.6.0")


compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect to Ganache the Rinkeby
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/7c5ce2a9748c42bea86051bf655cc3bd"))
chain_id = 4
my_address = "0x2655cAa6f91F1f5381dba4259192e66D871A075c"
private_key = os.getenv("PRIVATE_KEY")


# Create the contract in Python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
transaction = SimpleStorage.constructor().buildTransaction({"chainId": chain_id, "from": my_address, "nonce": nonce})

# 2. Sign a transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# 3. Send a transaction
print("Deploying Contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Contract Deployed")
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> simulate making the call
# Transact -> Make a state change
# Initial value of favorite number
print(simple_storage.functions.retrieve().call())
print("Updating Contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId": chain_id, "from": my_address, "nonce": nonce + 1
})
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(
    signed_store_txn.rawTransaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated Contract")
print(simple_storage.functions.retrieve().call())



