#!/bin/bash

# 設定捕捉 Ctrl+C 信號，關閉所有服務
trap 'echo -e "\n🛑 正在安全關閉所有服務..."; kill $P1 $P2 $P3 2>/dev/null; exit' SIGINT

clear
echo "======================================================"
echo "🚀 BlockWhisper 互動式自動啟動腳本"
echo "======================================================"

# 1. 啟動區塊鏈節點 (將輸出導向到 log 檔，保持終端機乾淨)
echo "📦 [1/4] 正在啟動 Hardhat 區塊鏈節點..."
cd blockchain
npx hardhat node > hardhat_node.log 2>&1 &
P1=$!
cd ..

# 等待 2 秒讓節點準備就緒
sleep 2
echo "✅ 本地節點已於 http://127.0.0.1:8545 啟動！(詳細日誌可查看 blockchain/hardhat_node.log)"

# 2. 自動執行 merkle_tree.py 計算 Root
echo ""
echo "🌳 [2/4] 正在為您計算最新的 Merkle Root..."
cd python_app
source venv/bin/activate
echo "------------------------------------------------------"
python merkle_tree.py
echo "------------------------------------------------------"
cd ..

# 3. 互動式輸入新地址
echo ""
echo "🦊 【Remix 部署設定提示】"
echo "  1. 請前往 https://remix.ethereum.org 編譯 CampusWall.sol"
echo "  2. ENVIRONMENT 選擇「Dev - Hardhat Provider」"
echo "  3. 複製上方產生的 Root 貼入 Deploy 欄位進行部署"
echo "  4. 部署成功後，請複製新產生的合約地址"
echo "======================================================"
read -p "👉 請貼上新的合約地址 (若無需更新請直接按 Enter): " NEW_ADDRESS

# 如果使用者有輸入新地址，就使用 Python 腳本自動替換 app.py 的內容
if [ -n "$NEW_ADDRESS" ]; then
    echo "🔄 正在自動更新 app.py 中的合約地址..."
    
    # 【修復處】：將 Bash 變數導出為環境變數，讓 Python 安全讀取
    export TARGET_ADDRESS="$NEW_ADDRESS"
    
    python3 -c "
import re, os
new_addr = os.environ.get('TARGET_ADDRESS')
with open('python_app/app.py', 'r', encoding='utf-8') as f:
    content = f.read()
# 使用正則表達式精準替換 CONTRACT_ADDRESS
content = re.sub(r'CONTRACT_ADDRESS\s*=\s*\".*?\"', f'CONTRACT_ADDRESS = \"{new_addr}\"', content)
with open('python_app/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
"
    echo "✅ 地址更新完成！"
else
    echo "⏩ 未輸入新地址，保留 app.py 原有設定繼續啟動。"
fi

# 4. 啟動後端與前端
echo ""
echo "⚙️  [3/4] 正在啟動 FastAPI 伺服器..."
cd python_app
uvicorn api:app --reload > /dev/null 2>&1 &
P2=$!

echo "🌐 [4/4] 正在啟動 Streamlit 網頁介面..."
streamlit run app.py &
P3=$!
cd ..

echo ""
echo "======================================================"
echo "🎉 所有服務已全面啟動！"
echo "💡 若要關閉專案，請在此視窗按下 [Ctrl + C]。"
echo "------------------------------------------------------"

# 等待所有背景程序
wait