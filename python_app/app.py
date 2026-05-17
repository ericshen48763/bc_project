import streamlit as st
import requests
from web3 import Web3
import json

# ================= 1. 系統設定參數 =================
API_URL = "http://127.0.0.1:8000/get_proof"
RPC_URL = "http://127.0.0.1:8545"

# ⚠️ 請填入你剛剛重新部署的新合約地址
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3" 

# ⚠️ 請填入新的 ABI (因為我們修改了 postMessage 函數和事件)
# ⚠️ 純淨版的新合約 ABI (已將 true/false 轉換為 Python 的 True/False)
CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "_merkleRoot", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "postId",
                "type": "uint256"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "parentId",
                "type": "uint256"
            },
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
            {"internalType": "string", "name": "message", "type": "string"},
            {"internalType": "uint256", "name": "parentId", "type": "uint256"},
            {"internalType": "bytes32", "name": "leaf", "type": "bytes32"},
            {"internalType": "bytes32[]", "name": "proof", "type": "bytes32[]"}
        ],
        "name": "postMessage",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "_newRoot", "type": "bytes32"}],
        "name": "updateMerkleRoot",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "merkleRoot",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "nextPostId",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# 初始化區塊鏈連線
w3 = Web3(Web3.HTTPProvider(RPC_URL))
checksum_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
contract = w3.eth.contract(address=checksum_address, abi=CONTRACT_ABI)

# 初始化 Session State
if "proof_data" not in st.session_state:
    st.session_state.proof_data = None

# ================= 2. 側邊欄導覽 (雙介面切換) =================
st.set_page_config(page_title="BlockWhisper", page_icon="🧱", layout="centered")

with st.sidebar:
    st.title("🧱 BlockWhisper")
    st.markdown("去中心化校園匿名牆")
    st.divider()
    # 這裡創造了兩個獨立的頁面！
    page = st.radio("請選擇操作介面：", ["🔑 身分驗證", "📜 留言板"])
    st.divider()
    
    # 模擬錢包選擇放在側邊欄，所有頁面共用
    accounts = w3.eth.accounts
    selected_account = st.selectbox("👛 模擬錢包地址", accounts)

# ================= 3. 介面 A：身分驗證 =================
if page == "🔑 身分驗證":
    st.header("🔑 領取匿名發文憑證")
    st.markdown("請輸入您的學號進行驗證。驗證成功後，系統將核發您的專屬 Merkle Proof。")
    
    student_id = st.text_input("輸入學號:", placeholder="例如: 411185003")
    
    if st.button("領取通行證", type="primary"):
        if student_id:
            try:
                res = requests.get(f"{API_URL}/{student_id}")
                if res.status_code == 200:
                    st.session_state.proof_data = res.json()
                    st.success("✅ 憑證獲取成功！您現在可以切換到「留言板」發文了。")
                else:
                    st.error("❌ 驗證失敗：查無此學號或不在白名單內。")
            except Exception as e:
                st.error("無法連線到伺服器。")
        else:
            st.warning("請先輸入學號")

# ================= 4. 介面 B：留言板 =================
elif page == "📜 留言板":
    st.header("📜 校園匿名留言板")
    
    # 🚨 【新增：門禁防護系統】 🚨
    if not st.session_state.proof_data:
        st.warning("🔒 存取被拒絕：您尚未領取發文通行證！")
        st.info("👉 請點擊左側欄選單回到「🔑 身分驗證」，輸入有效學號領取憑證後，即可解鎖留言板。")
        st.stop() # 關鍵指令：停止執行這行以下的所有程式碼，讓使用者甚麼都看不到！

    # --- 下面是原本的留言板內容 (只有驗證通過才會執行到這裡) ---
    
    # --- 發表新貼文區塊 ---
    with st.container(border=True):
        st.subheader("✍️ 發表新貼文")
        new_post_msg = st.text_area("想說點什麼？", placeholder="發布一篇新的靠北文...")
        
        if st.button("發布貼文 🚀", use_container_width=True):
            if new_post_msg:
                leaf = st.session_state.proof_data["leaf"]
                proof = st.session_state.proof_data["proof"]
                try:
                    with st.spinner('上鏈中...'):
                        tx_hash = contract.functions.postMessage(
                            new_post_msg, 0, bytes.fromhex(leaf[2:]), [bytes.fromhex(p[2:]) for p in proof]
                        ).transact({'from': selected_account})
                        w3.eth.wait_for_transaction_receipt(tx_hash)
                        st.success("🎉 貼文發布成功！請點擊下方刷新。")
                except Exception as e:
                    st.error(f"❌ 交易失敗：{e}")

    st.divider()
    
    # --- 歷史留言牆區塊 ---
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("最新動態")
    with col2:
        refresh = st.button("🔄 刷新")

    try:
        events = contract.events.ConfessionPosted.get_logs(from_block=0, to_block='latest')
        
        posts = []
        comments_map = {} 
        
        for event in events:
            args = event['args']
            if args['parentId'] == 0:
                posts.append(args)
                comments_map[args['postId']] = []
            else:
                if args['parentId'] in comments_map:
                    comments_map[args['parentId']].append(args)

        if len(posts) == 0:
            st.info("目前還沒有任何人發文，搶頭香吧！")
        else:
            for post in reversed(posts):
                post_id = post['postId']
                
                with st.container(border=True):
                    st.markdown(f"### 📝 貼文 #{post_id}")
                    st.write(post['message'])
                    
                    comments = comments_map.get(post_id, [])
                    if comments:
                        st.divider()
                        for c in comments:
                            st.caption(f"💬 回覆: {c['message']}")
                    
                    with st.expander("回覆此貼文..."):
                        reply_msg = st.text_input("輸入您的回覆：", key=f"input_{post_id}")
                        if st.button("發送留言", key=f"btn_{post_id}"):
                            if reply_msg:
                                leaf = st.session_state.proof_data["leaf"]
                                proof = st.session_state.proof_data["proof"]
                                try:
                                    with st.spinner('回覆上鏈中...'):
                                        tx_hash = contract.functions.postMessage(
                                            reply_msg, post_id, bytes.fromhex(leaf[2:]), [bytes.fromhex(p[2:]) for p in proof]
                                        ).transact({'from': selected_account})
                                        w3.eth.wait_for_transaction_receipt(tx_hash)
                                        st.success("回覆成功！請重新整理頁面。")
                                except Exception as e:
                                    st.error("失敗")
    except Exception as e:
        st.error(f"讀取資料失敗：{e}")