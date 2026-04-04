from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from merkle_tree import MerkleTree  # 引入我們剛剛寫好的 Merkle Tree 模組

# 初始化 FastAPI 應用程式
app = FastAPI(title="Campus Wall API")

# 設定 CORS，允許未來 Streamlit 前端網頁來呼叫這個 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模擬後端資料庫中的「全校有效名單」(隱私資料，不上鏈)
# 我們把你們兩個的學號都加進白名單測試
SECRET_STUDENT_LIST = ["411185003", "411185039", "411185999", "411185888"]

# 伺服器啟動時，直接在記憶體中建構出 Merkle Tree
tree = MerkleTree(SECRET_STUDENT_LIST)

@app.get("/")
def read_root():
    return {"message": "區塊鏈校園牆 API 伺服器運行中！"}

@app.get("/get_proof/{student_id}")
def get_proof(student_id: str):
    """
    前端傳入學號，後端驗證後核發 Proof
    """
    # 清除輸入時可能不小心多打的空白鍵
    student_id = student_id.strip()

    # 1. 檢查學號是否在白名單內
    if student_id not in SECRET_STUDENT_LIST:
        raise HTTPException(status_code=403, detail="此學號不具備發文資格或不存在。")
    
    # 2. 生成發文所需的密碼學參數
    proof = tree.get_proof(student_id)
    
    # 【修復重點】：將原本的 _hash 改為 _hash_string
    leaf = tree._hash_string(student_id)
    root = tree.get_root()
    
    return {
        "status": "success",
        "student_id": student_id,
        "root": root,
        "leaf": leaf,
        "proof": proof
    }