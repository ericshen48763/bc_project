# 🧱 BlockWhisper 開發協作指南 (Internal README)

哈囉！這裡是 BlockWhisper 的核心程式碼庫。
目前的進度已經成功打通了「後端 Merkle Proof 發放」以及「前端與智能合約上鏈互動」的完整流程。

請在開發或測試前，先詳細閱讀以下環境建置。

---

## 📂 資料夾結構說明

專案主要分為兩個獨立的環境（區塊鏈與 Python 後端）：
```
📦 BlockWhisper_Project
 ┣ 📂 blockchain/        # 智能合約與 Hardhat 開發環境
 ┃ ┣ 📂 contracts/       # Solidity 原始碼 (CampusWall.sol)
 ┃ ┣ 📂 artifacts/       # 📌 重要：編譯後產生的 ABI 與 Bytecode 都在這裡
 ┃ ┣ 📜 hardhat.config.ts# Hardhat 設定檔 (我們已拔除多餘套件，純編譯)
 ┃ ┗ 📜 package.json     # Node.js 依賴清單
 ┃
 ┗ 📂 python_app/        # 後端 API 與前端網頁
   ┣ 📜 merkle_tree.py   # 核心密碼學引擎 (使用 Keccak-256)
   ┣ 📜 api.py           # FastAPI 伺服器 (負責核發 Proof)
   ┣ 📜 app.py           # Streamlit 前端介面
   ┗ 📜 requirements.txt # Python 套件清單 (請確認安裝 web3 v6+)
```
🚀 本地端開發環境啟動流程
測試完整系統需要開啟 3 個獨立的終端機視窗。請依照以下順序啟動：

Terminal 1: 啟動本地區塊鏈節點
```
cd blockchain
npm install
npx hardhat node
```
⚠️ 注意：啟動後會跑出一堆測試帳號，請保持這個視窗開啟。預設 RPC URL 為 http://127.0.0.1:8545。

📌 部署合約：目前採用 Remix 部署至 Hardhat 本地節點的方式。部署後，請務必將「合約地址」更新到 python_app/app.py 中。

Terminal 2: 啟動憑證核發伺服器 (API)
```
cd python_app
# 進入虛擬環境
source venv/bin/activate  # Windows 請用 venv\Scripts\activate
pip install -r requirements.txt
uvicorn api:app --reload
```
⚠️ 注意：API 運行於 http://127.0.0.1:8000。測試名單寫死在 api.py 的 SECRET_STUDENT_LIST 中。

Terminal 3: 啟動前端網頁介面
```
cd python_app
source venv/bin/activate
streamlit run app.py
```
