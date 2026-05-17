import json
from web3 import Web3

# 1. 連線到本地的 Hardhat 節點
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# 確認連線成功
if not w3.is_connected():
    print("無法連線到 Hardhat 節點，請確認 npx hardhat node 已啟動")
    exit()

# 2. 設定部署帳號 (自動抓取 Hardhat 提供的第一組測試帳號)
deployer_account = w3.eth.accounts[0]
w3.eth.default_account = deployer_account
print(f"使用帳號部署: {deployer_account}")

# 3. 讀取編譯好的合約 JSON 檔 
# (請將路徑替換成你實際的 artifacts JSON 路徑)
with open("artifacts/contracts/BlockWhisper.sol/BlockWhisper.json", "r", encoding="utf-8") as f:
    contract_data = json.load(f)

abi = contract_data['abi']
bytecode = contract_data['bytecode']

# 4. 建立合約物件
WhisperContract = w3.eth.contract(abi=abi, bytecode=bytecode)

# 5. 發送部署交易
print("正在將合約部署至區塊鏈...")
# 如果你的合約 constructor() 需要傳參數，請寫在 constructor(參數1, 參數2) 裡面
tx_hash = WhisperContract.constructor().transact()

# 6. 等待區塊鏈打包，並取得最終的合約地址
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("========================================")
print("🎉 部署成功！")
print(f"合約地址: {tx_receipt.contractAddress}")
print("請將此地址複製到 FastAPI 與 Streamlit 的設定中")
print("========================================")