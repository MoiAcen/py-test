@echo off
REM 金鑰產生與密碼加密工具
REM 用法:
REM   keygen.bat              產生新的 Fernet 金鑰
REM   keygen.bat encrypt      加密資料庫密碼（互動式）
REM   keygen.bat decrypt      解密確認（互動式）
REM
REM 註: FERNET_KEY 由 python-dotenv 自 .env 自動載入，毋需手動 export。

setlocal enabledelayedexpansion
cd /d "%~dp0"

set ACTION=%~1
if "%ACTION%"=="" set ACTION=keygen

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
set /p DB_PASS=請輸入要加密的資料庫密碼:
echo.
REM Python CLI 輸出純密文（無前綴），以引數傳入確保不含尾端空白
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
