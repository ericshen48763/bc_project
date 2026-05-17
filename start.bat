@echo off
chcp 65001 > nul
echo ======================================================
echo 🚀 BlockWhisper 終極一鍵啟動腳本 (Windows Auto-Deploy 版)
echo ======================================================

:: 1. 啟動區塊鏈節點 (開啟新的視窗執行)
echo 📦 [1/4] 正在啟動 Hardhat 區塊鏈節點...
cd blockchain
start "Hardhat Node" cmd /c "npx hardhat node"

:: 等待 3 秒讓節點完全啟動
timeout /t 3 /nobreak > nul
echo ✅ 本地節點已啟動！(http://127.0.0.1:8545)

:: 2. 自動編譯智能合約
echo 🔨 正在編譯智能合約...
call npx hardhat compile > nul
cd ..

:: 3. 執行 Python 自動部署腳本
echo.
echo 🤖 [2/4] 正在執行自動部署與更新 app.py...
cd python_app
call venv\Scripts\activate.bat
echo ------------------------------------------------------
python deploy.py
echo ------------------------------------------------------

:: 4. 啟動後端與前端 (分別開啟新視窗)
echo.
echo ⚙️  [3/4] 正在啟動 FastAPI 伺服器...
start "FastAPI Server" cmd /c "call venv\Scripts\activate.bat && uvicorn api:app --reload"

echo 🌐 [4/4] 正在啟動 Streamlit 網頁介面...
start "Streamlit App" cmd /c "call venv\Scripts\activate.bat && streamlit run app.py"
cd ..

echo.
echo ======================================================
echo 🎉 所有服務已全面啟動！
echo 💡 注意：系統已幫您開啟了三個新的黑色視窗。
echo 💡 若要關閉系統，請直接將那三個視窗打叉關閉即可。
echo ------------------------------------------------------
pause