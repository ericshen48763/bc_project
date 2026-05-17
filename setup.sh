#!/bin/bash

# 當發生錯誤時立即停止腳本
set -e

echo "======================================================"
echo "🚀 正在為系統初始化開發環境..."
echo "======================================================"

# 1. 建置 Node.js (Hardhat) 環境
echo ""
echo "📦 [1/2] 正在安裝區塊鏈智能合約相依套件 (Node.js)..."
if [ -d "blockchain" ]; then
    cd blockchain
    npm install
    cd ..
    echo "✅ 區塊鏈環境建置完成！"
else
    echo "⚠️ 找不到 blockchain 資料夾，跳過此步驟。"
fi

# 2. 建置 Python 虛擬環境
echo ""
echo "🐍 [2/2] 正在建立 Python 虛擬環境與安裝套件..."
if [ -d "python_app" ]; then
    cd python_app
    
    # 檢查是否已經有 venv，沒有的話就建立一個
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✨ 虛擬環境 (venv) 建立成功！"
    fi

    # 啟動虛擬環境 (相容 Mac/Linux 與 Windows Git Bash)
    source venv/bin/activate
    
    # 更新 pip 並安裝套件
    echo "⬇️ 正在安裝 requirements.txt 中的套件..."
    python -m pip install --upgrade pip > /dev/null
    pip install -r requirements.txt
    
    # 離開虛擬環境回到外層
    deactivate
    cd ..
    echo "✅ Python 環境建置完成！"
else
    echo "⚠️ 找不到 python_app 資料夾，跳過此步驟。"
fi

echo ""
echo "======================================================"
echo "🎉 所有環境建置完畢！"
echo "👉 下一步：請設定您的 .env 檔案，然後執行 ./start.sh 啟動系統！"
echo "======================================================"