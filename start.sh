#!/bin/bash

# 設定捕捉 Ctrl+C 信號，關閉所有服務
trap 'echo -e "\n🛑 正在安全關閉所有服務..."; kill $P1 $P2 $P3 2>/dev/null; exit' SIGINT

clear
echo "======================================================"
echo "🚀 BlockWhisper 終極一鍵啟動腳本 (Auto-Deploy 版)"
echo "======================================================"

# 1. 啟動區塊鏈節點
echo "📦 [1/4] 正在啟動 Hardhat 區塊鏈節點..."
cd blockchain
npx hardhat node > hardhat_node.log 2>&1 &
P1=$!

# 等待 3 秒讓節點完全啟動
sleep 3 
echo "✅ 本地節點已啟動！(http://127.0.0.1:8545)"

# 2. 自動編譯智能合約 (確保拿到最新的 ABI)
echo "🔨 正在編譯智能合約..."
npx hardhat compile > /dev/null 2>&1
cd ..

# 3. 執行 Python 自動部署腳本 (算 Root + 部署合約 + 更新 app.py 一氣呵成)
echo ""
echo "🤖 [2/4] 正在計算 Merkle Root 並自動部署智能合約..."
cd python_app
source venv/bin/activate
echo "------------------------------------------------------"
python deploy.py
echo "------------------------------------------------------"

# 4. 啟動後端與前端
echo ""
echo "⚙️  [3/4] 正在啟動 FastAPI 伺服器..."
uvicorn api:app --reload > /dev/null 2>&1 &
P2=$!

echo "🌐 [4/4] 正在啟動 Streamlit 網頁介面..."
streamlit run app.py &
P3=$!
cd ..

echo ""
echo "======================================================"
echo "🎉 所有服務已全面啟動！不再需要手動開啟 Remix 了！"
echo "💡 若要關閉專案，請在此視窗按下 [Ctrl + C]。"
echo "------------------------------------------------------"

# 等待所有背景程序
wait