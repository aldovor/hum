from web3 import Web3
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Inisialisasi koneksi
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
wallet_address = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
contract_address = Web3.to_checksum_address("0xa18f6FCB2Fd4884436d10610E69DB7BFa1bFe8C7")

# ABI kontrak dari yang kamu kirim
contract_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "account", "type": "address"}
        ],
        "name": "hasRole",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "CLAIMER_ROLE",
        "outputs": [],
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
]  # Ganti dengan ABI lengkap yang kamu punya

# Inisialisasi kontrak
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Role hash default (gunakan ini jika kontrak mengikuti pola AccessControl dari OpenZeppelin)
CLAIMER_ROLE = w3.keccak(text="CLAIMER_ROLE")

# Cek jika wallet memiliki role CLAIMER_ROLE
has_role = contract.functions.hasRole(CLAIMER_ROLE, wallet_address).call()

# Fungsi klaim reward jika wallet memiliki role CLAIMER_ROLE
def claim_rewards():
    try:
        # Periksa reward yang tersedia
        daily = contract.functions.dailyRewardsAvailable(wallet_address).call()
        genesis = contract.functions.genesisRewardsAvailable(wallet_address).call()

        print(f"🎁 Daily reward tersedia: {daily}")
        print(f"🌱 Genesis reward tersedia: {genesis}")

        # Klaim reward jika ada yang tersedia
        if daily > 0:
            # Panggil fungsi klaim reward untuk daily
            tx = contract.functions.claimDailyRewards().buildTransaction({
                'from': wallet_address,
                'gas': 200000,  # Sesuaikan gas limit
                'gasPrice': w3.toWei('10', 'gwei'),
                'nonce': w3.eth.getTransactionCount(wallet_address),
            })
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=os.getenv("PRIVATE_KEY"))
            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print(f"💸 Klaim Daily reward berhasil! Tx hash: {tx_hash.hex()}")

        if genesis > 0:
            # Panggil fungsi klaim reward untuk genesis
            tx = contract.functions.claimGenesisRewards().buildTransaction({
                'from': wallet_address,
                'gas': 200000,  # Sesuaikan gas limit
                'gasPrice': w3.toWei('10', 'gwei'),
                'nonce': w3.eth.getTransactionCount(wallet_address),
            })
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=os.getenv("PRIVATE_KEY"))
            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print(f"🌱 Klaim Genesis reward berhasil! Tx hash: {tx_hash.hex()}")

    except Exception as e:
        print(f"❌ Terjadi kesalahan saat klaim reward: {e}")

# Mengecek role dan klaim jika ada role CLAIMER_ROLE
if has_role:
    print("🔐 Wallet memiliki CLAIMER_ROLE, dapat melakukan klaim reward!")
    claim_rewards()
else:
    print("❌ Wallet tidak memiliki CLAIMER_ROLE, tidak dapat melakukan klaim reward.")
