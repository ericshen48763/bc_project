import json
import subprocess
import re
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
contract_path = "../blockchain/artifacts/contracts/CampusWall.sol/CampusWall.json"

with open(contract_path, "r", encoding="utf-8") as f:
    contract_data = json.load(f)

abi = contract_data['abi']
bytecode = contract_data['bytecode']

# 4. 建立合約物件
WhisperContract = w3.eth.contract(abi=abi, bytecode=bytecode)

# 5. 計算並取得真實的 Merkle Root
print("🌳 正在計算真實的 Merkle Root...")
try:
    # 使用 subprocess 執行你們原本計算 Root 的檔案
    result = subprocess.run(['python', 'merkle_tree.py'], capture_output=True, text=True)
    
    # 從終端機輸出中尋找 0x 開頭的字串作為 Root
    real_root_hex = None
    for line in result.stdout.splitlines():
        if line.strip().startswith("0x"):
            real_root_hex = line.strip()
            break
            
    if not real_root_hex:
        print("❌ 錯誤：無法從 merkle_tree.py 的輸出中找到 0x 開頭的 Merkle Root！")
        print("請確認 merkle_tree.py 執行後會印出 Root。")
        exit()
        
    print(f"✅ 成功取得真實 Root: {real_root_hex}")
    # 將十六進位字串轉換為合約能接受的 bytes32 格式
    real_root_bytes = Web3.to_bytes(hexstr=real_root_hex)
    
except Exception as e:
    print(f"❌ 取得 Root 時發生系統錯誤: {e}")
    exit()

# 6. 發送部署交易
print("正在將合約部署至區塊鏈...")
# 將「真實的 Root」放進 constructor 中進行部署！
tx_hash = WhisperContract.constructor(real_root_bytes).transact()

# 7. 等待區塊鏈打包，並取得最終的合約地址
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
new_address = tx_receipt.contractAddress

print("========================================")
print("🎉 部署成功！")
print(f"合約地址: {new_address}")
print("========================================")

# 8. 自動更新 app.py 中的合約地址
print("🔄 正在自動更新 app.py...")
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用正則表達式精準尋找並替換 CONTRACT_ADDRESS = "..."
    content = re.sub(r'CONTRACT_ADDRESS\s*=\s*["\'].*?["\']', f'CONTRACT_ADDRESS = "{new_address}"', content)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ app.py 更新完成！現在可以直接在網頁上測試發文了！")
except FileNotFoundError:
    print("⚠️ 找不到 app.py，請手動複製上方地址並更新您的設定檔。")