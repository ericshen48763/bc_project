@echo off
chcp 65001 > nul

echo ======================================================
echo 系統環境初始化 (Windows 版)
echo ======================================================

echo.
echo [1/2] 正在安裝區塊鏈智能合約相依套件 (Node.js)...
if exist "blockchain" (
    cd blockchain
    :: 【修正 1】：加入 --legacy-peer-deps 強制安裝，解決版本衝突
    call npm install --legacy-peer-deps
    cd ..
    echo [成功] 區塊鏈環境建置完成！
) else (
    echo [警告] 找不到 blockchain 資料夾，跳過此步驟。
)

echo.
echo [2/2] 正在建立 Python 虛擬環境與安裝套件...
if exist "python_app" (
    cd python_app
    
    if not exist "venv" (
        python -m venv venv
        echo [成功] 虛擬環境 venv 建立成功！
    )

    :: 【修正 2】：移除所有表情符號，避免 Windows CMD 亂碼崩潰
    echo 正在安裝 requirements.txt 中的套件...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip > nul
    pip install -r requirements.txt
    
    call venv\Scripts\deactivate.bat
    cd ..
    echo [成功] Python 環境建置完成！
) else (
    echo [警告] 找不到 python_app 資料夾，跳過此步驟。
)

echo.
echo ======================================================
echo [完成] 所有環境建置完畢！
echo 下一步：請設定您的 .env 檔案，然後執行 start.bat 啟動系統！
echo ======================================================
pause