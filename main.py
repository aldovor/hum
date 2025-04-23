from web3 import Web3
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Inisialisasi koneksi
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
wallet_address = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
contract_address = Web3.to_checksum_address("0xa18f6FCB2Fd4884436d10610E69DB7BFa1bFe8C7")

# ABI kontrak (Pastikan kamu sudah mendapatkan ABI lengkap kontrak)
contract_abi = [
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
        "name": "dailyRewardsAvailable",
        "outputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
        "name": "genesisRewardsAvailable",
        "outputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"}, {"internalType": "address", "name": "account", "type": "address"}],
        "name": "hasRole",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "claimReward",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Inisialisasi kontrak
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Cek reward yang tersedia
daily = contract.functions.dailyRewardsAvailable(wallet_address).call()
genesis = contract.functions.genesisRewardsAvailable(wallet_address).call()

# Role hash default (gunakan ini jika kontrak mengikuti pola AccessControl dari OpenZeppelin)
CLAIMER_ROLE = w3.keccak(text="CLAIMER_ROLE")  # Ganti sesuai kebutuhan
has_role = contract.functions.hasRole(CLAIMER_ROLE, wallet_address).call()

print(f"🎁 Daily reward tersedia: {daily}")
print(f"🌱 Genesis reward tersedia: {genesis}")
print(f"🔐 Wallet punya CLAIMER_ROLE: {has_role}")

# Mengecek jika wallet memiliki role dan reward yang tersedia, lalu klaim reward
if has_role:
    if daily > 0 or genesis > 0:
        # Build transaksi untuk klaim
        nonce = w3.eth.get_transaction_count(wallet_address)
        gas_price = w3.eth.gas_price

        tx = contract.functions.claimReward().build_transaction({
            'from': wallet_address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': gas_price,
            'chainId': w3.eth.chain_id
        })

        # Tandatangani transaksi
        private_key = os.getenv("PRIVATE_KEY")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)

        # Kirim transaksi
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✅ Transaksi terkirim! Hash: {tx_hash.hex()}")
    else:
        print("❌ Tidak ada reward yang tersedia untuk diklaim.")
else:
    print("❌ Wallet tidak memiliki peran untuk melakukan klaim.")
