@echo off
REM 金鑰產生與密碼加密工具
REM 用法:
REM   keygen.bat              產生新的 Fernet 金鑰
REM   keygen.bat encrypt      加密資料庫密碼（互動式）
REM   keygen.bat decrypt      解密確認（互動式）

setlocal enabledelayedexpansion

set ACTION=%~1
if "%ACTION%"=="" set ACTION=keygen

REM 讀取 .env（若存在）
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "ln=%%A"
        if not "!ln:~0,1!"=="#" if not "%%A"=="" set "%%A=%%B"
    )
)

if "%ACTION%"=="keygen" goto :keygen
if "%ACTION%"=="encrypt" goto :encrypt
if "%ACTION%"=="decrypt" goto :decrypt
goto :usage

:keygen
echo ========================================
echo  Fernet 金鑰產生工具
echo ========================================
python -m config.crypto
echo.
echo [提示] 將上方 FERNET_KEY 與 ORACLE_PASSWORD_ENCRYPTED 填入 .env 檔案
goto :end

:encrypt
echo ========================================
echo  資料庫密碼加密工具
echo ========================================
if "%FERNET_KEY%"=="" (
    echo [錯誤] 未找到 FERNET_KEY，請先設定 .env 或執行: keygen.bat
    exit /b 1
)
set /p DB_PASS=請輸入要加密的資料庫密碼:
echo.
for /f "delims=" %%R in ('python -m config.crypto encrypt "!DB_PASS!"') do set ENCRYPTED=%%R
echo [結果] 加密後密文:
echo   ORACLE_PASSWORD_ENCRYPTED=!ENCRYPTED!
echo.
echo [提示] 請將上方密文填入 .env 的 ORACLE_PASSWORD_ENCRYPTED
goto :end

:decrypt
echo ========================================
echo  密文解密確認工具
echo ========================================
if "%FERNET_KEY%"=="" (
    echo [錯誤] 未找到 FERNET_KEY，請先設定 .env
    exit /b 1
)
set /p CIPHER=請輸入要解密的密文:
echo.
for /f "delims=" %%R in ('python -m config.crypto decrypt "!CIPHER!"') do set PLAIN=%%R
echo [結果] 解密後明文: !PLAIN!
goto :end

:usage
echo 用法:
echo   keygen.bat              產生新的 Fernet 金鑰
echo   keygen.bat encrypt      加密資料庫密碼
echo   keygen.bat decrypt      解密確認
exit /b 1

:end
endlocal
