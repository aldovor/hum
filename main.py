from web3 import Web3
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get data from .env
rpc_url = os.getenv("RPC_URL")
wallet_address = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
private_key = os.getenv("PRIVATE_KEY")

# Connect to RPC
w3 = Web3(Web3.HTTPProvider(rpc_url))

# Check connection
if not w3.is_connected():
    raise ConnectionError("❌ Failed to connect to RPC from .env.")

# Contract address
contract_address = w3.to_checksum_address("0xa18f6FCB2Fd4884436d10610E69DB7BFa1bFe8C7")

# Minimal ABI for claimReward
contract_abi = [
    {
        "inputs": [],
        "name": "claimReward",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Initialize contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Build transaction
nonce = w3.eth.get_transaction_count(wallet_address)
gas_price = w3.eth.gas_price

tx = contract.functions.claimReward().build_transaction({
    'from': wallet_address,
    'nonce': nonce,
    'gas': 200000,
    'gasPrice': gas_price,
    'chainId': w3.eth.chain_id
})

# Sign and send the transaction
signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print(f"✅ Transaction sent! Hash: {tx_hash.hex()}")
