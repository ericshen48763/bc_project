import streamlit as st
import requests
from web3 import Web3
import json

# ================= 1. 系統設定參數 =================
API_URL = "http://127.0.0.1:8000/get_proof"
RPC_URL = "http://127.0.0.1:8545" # Hardhat 本地節點

# ⚠️ 請把你在步驟一複製的合約地址貼到這裡
CONTRACT_ADDRESS = "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0" 

# ⚠️ 請把你在步驟一複製的 ABI (那一大串 JSON) 貼到這裡
# ⚠️ 純淨版的合約 ABI (已經轉換為 Python 支援的格式)
# ⚠️ 純淨版的合約 ABI (已將 false 轉換為 Python 的 False)
CONTRACT_ABI = [
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "_merkleRoot",
				"type": "bytes32"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "string",
				"name": "message",
				"type": "string"
			}
		],
		"name": "ConfessionPosted",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "message",
				"type": "string"
			},
			{
				"internalType": "bytes32",
				"name": "leaf",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32[]",
				"name": "proof",
				"type": "bytes32[]"
			}
		],
		"name": "postMessage",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "_newRoot",
				"type": "bytes32"
			}
		],
		"name": "updateMerkleRoot",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "merkleRoot",
		"outputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

# ================= 2. 初始化區塊鏈連線 =================
w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# 初始化 Streamlit 狀態 (用來暫存拿到的通行證)
if "proof_data" not in st.session_state:
    st.session_state.proof_data = None

st.set_page_config(page_title="BlockWhisper 校園牆", page_icon="🧱")
st.title("🧱 BlockWhisper 匿名校園牆")
st.markdown("基於以太坊與 Merkle Tree 的抗審查發文系統")
st.divider()

# ================= 3. 介面：身分驗證區 =================
st.subheader("🔑 第一步：取得發文憑證")
student_id = st.text_input("輸入學號 (僅向後端驗證，絕對不會上鏈):", placeholder="例如: 411185003")

if st.button("領取通行證"):
    if student_id:
        try:
            res = requests.get(f"{API_URL}/{student_id}")
            if res.status_code == 200:
                st.session_state.proof_data = res.json()
                st.success("✅ 憑證獲取成功！你現在可以匿名發文了。")
            else:
                st.error("❌ 驗證失敗：查無此學號或不在白名單內。")
        except Exception as e:
            st.error("無法連線到 FastAPI 伺服器，請確認伺服器是否已啟動。")
    else:
        st.warning("請先輸入學號")

# ================= 4. 介面：發文區 =================
st.divider()
st.subheader("✍️ 第二步：匿名發布留言")

# 這裡我們用 Hardhat 提供的測試帳號來「模擬」MetaMask 錢包
accounts = w3.eth.accounts
selected_account = st.selectbox("模擬你的加密錢包地址 (負責付手續費):", accounts)

message = st.text_area("輸入你的靠北內容：", placeholder="學餐的便當又漲價了！")

if st.button("發布到區塊鏈 🚀"):
    if not st.session_state.proof_data:
        st.warning("⚠️ 請先在上方領取通行證！")
    elif not message:
        st.warning("⚠️ 總得說點什麼吧？")
    else:
        leaf = st.session_state.proof_data["leaf"]
        proof = st.session_state.proof_data["proof"]
        
        try:
            with st.spinner('正在與智能合約交互中，請稍候...'):
                # 呼叫智能合約的 postMessage 函數
                tx_hash = contract.functions.postMessage(message, bytes.fromhex(leaf[2:]), [bytes.fromhex(p[2:]) for p in proof]).transact({
                    'from': selected_account
                })
                # 等待區塊鏈確認
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                st.success(f"🎉 發布成功！這則留言已被永久刻在區塊鏈上。")
                st.info(f"交易 Hash: {tx_hash.hex()}")
        except Exception as e:
            st.error(f"❌ 智能合約拒絕了交易，原因可能為憑證無效或重複發文。錯誤細節：{e}")

# ================= 5. 介面：展示區 =================
st.divider()
st.subheader("📜 最新留言牆")

if st.button("刷新留言板 🔄"):
    try:
        # 使用最新版 Web3.py 推薦的 get_logs() 來抓取歷史事件
        events = contract.events.ConfessionPosted.get_logs(from_block=0, to_block='latest')
        
        if len(events) == 0:
            st.info("目前還沒有任何人發文，搶頭香吧！")
        else:
            # 將事件反轉，讓最新發布的留言顯示在最上面
            for event in reversed(events):
                msg = event['args']['message']
                st.chat_message("user").write(msg)
                
    except Exception as e:
        st.error(f"讀取留言失敗，錯誤細節：{e}")