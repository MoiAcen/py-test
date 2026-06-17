@echo off
chcp 65001 >nul
REM 企業資料平台 - Windows 啟動腳本
REM 用法: startup.bat [PORT]

setlocal

REM 設定預設埠號，可透過第一個參數覆蓋
if "%~1"=="" (
    set PORT=8501
) else (
    set PORT=%~1
)

REM 讀取 .env 檔案（如果存在）
if exist ".env" (
    echo [INFO] 讀取 .env 設定檔...
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "line=%%A"
        if not "!line:~0,1!"=="#" (
            if not "%%A"=="" set "%%A=%%B"
        )
    )
)

echo [INFO] 啟動企業資料平台...
echo [INFO] 埠號: %PORT%
echo [INFO] 應用模式: %APP_MODE%
echo [INFO] 瀏覽器請開啟: http://localhost:%PORT%
echo.

streamlit run app.py ^
    --server.port %PORT% ^
    --server.address 0.0.0.0 ^
    --server.headless true ^
    --browser.gatherUsageStats false

endlocal
