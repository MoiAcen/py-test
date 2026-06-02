# 企業資料平台

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red?logo=streamlit)
![Azure AD](https://img.shields.io/badge/Azure%20AD-Entra%20ID-0078D4?logo=microsoftazure)
![Oracle](https://img.shields.io/badge/Oracle-DB-F80000?logo=oracle)

企業級資料平台，整合 Azure Entra ID 單一登入、角色型存取控制（RBAC）與 Oracle 資料庫連線，支援 Demo 示範模式與 Azure DevOps 部署。

---

## 功能特色

- **Azure Entra ID 單一登入** — 基於 MSAL OAuth2 授權碼流程，企業帳號直接登入
- **角色型存取控制 (RBAC)** — admin / manager / user / guest 四級權限分層管理
- **Oracle 資料庫連線** — oracledb thin 模式，免安裝 Oracle Client
- **Fernet 對稱加密** — 資料庫密碼加密儲存，避免明文出現在設定檔
- **Demo 示範模式** — 無需真實 Azure AD，可直接選角色體驗各頁面
- **Azure DevOps Pipeline** — 內建 CI/CD 流程，支援 Replace Tokens 注入環境變數

---

## 專案結構

```
py-test/
├── app.py                  # Streamlit 主入口
├── requirements.txt        # Python 相依套件
├── startup.sh              # Azure App Service 啟動腳本
├── azure-pipelines.yml     # Azure DevOps CI/CD Pipeline
├── .env.example            # 環境變數說明範本
├── .env.tokens             # Replace Tokens 部署範本（含 #{VAR}# 占位符）
├── config/
│   ├── settings.py         # 集中管理所有設定項
│   └── crypto.py           # Fernet 加密解密工具（含 CLI）
├── auth/
│   ├── entra.py            # Azure Entra MSAL 認證流程
│   └── roles.py            # 角色與權限定義
├── db/
│   └── oracle.py           # Oracle 資料庫連線與查詢
├── utils/
│   └── session.py          # Streamlit Session State 管理
└── pages/
    ├── admin.py            # 管理員控制台
    ├── manager.py          # 經理儀表板
    ├── user.py             # 個人儀表板
    └── guest.py            # 訪客首頁
```

---

## 快速開始

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 產生加密金鑰並加密資料庫密碼

```bash
python -m config.crypto
```

執行後會輸出 `FERNET_KEY` 和範例密文，將其填入 `.env`。

### 3. 建立環境變數檔案

```bash
cp .env.example .env
```

編輯 `.env`，填入 Azure AD 與 Oracle 相關設定。

### 4. 啟動應用程式

```bash
streamlit run app.py
```

瀏覽器開啟 [http://localhost:8501](http://localhost:8501)。

---

## 環境變數說明

| 變數名稱 | 說明 | 範例 |
|---|---|---|
| `AZURE_CLIENT_ID` | Azure AD 應用程式（用戶端）識別碼 | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_CLIENT_SECRET` | Azure AD 用戶端密碼 | `your-secret-value` |
| `AZURE_TENANT_ID` | Azure AD 租用戶識別碼 | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_REDIRECT_URI` | OAuth2 回呼 URI（需在 Azure AD 應用程式中註冊） | `http://localhost:8501` |
| `AZURE_GROUP_ROLE_MAP` | Azure AD 群組 ID 對應角色（逗號分隔） | `group-id-1:admin,group-id-2:manager` |
| `ORACLE_HOST` | Oracle 資料庫主機名稱或 IP | `db.example.com` |
| `ORACLE_PORT` | Oracle 監聽埠號 | `1521` |
| `ORACLE_SERVICE` | Oracle 服務名稱 | `XEPDB1` |
| `ORACLE_USER` | Oracle 資料庫用戶名稱 | `system` |
| `ORACLE_PASSWORD_ENCRYPTED` | 使用 Fernet 加密後的資料庫密碼 | `gAAAAAB...` |
| `FERNET_KEY` | Fernet 對稱加密金鑰（Base64） | `abc123...=` |
| `APP_MODE` | 應用模式：`demo` 或 `production` | `demo` |

---

## Demo 模式說明

當 `APP_MODE=demo` 時，應用程式進入示範模式：

- 不需要真實 Azure AD 設定
- 頁面頂部顯示角色選擇器，可直接切換 admin / manager / user / guest
- 所有資料均為模擬資料，不會連線至真實資料庫
- 適用於本機開發、UI 測試與展示

切換為生產模式：將 `.env` 中 `APP_MODE` 改為 `production`，並填入所有 Azure AD 與 Oracle 設定。

---

## 角色說明

| 角色 | 顯示名稱 | 可存取頁面 | 說明 |
|---|---|---|---|
| `admin` | 管理員 Admin | 管理員控制台、經理儀表板、個人頁面 | 全功能存取，含用戶管理與系統設定 |
| `manager` | 經理 Manager | 經理儀表板、個人頁面 | 可查看團隊績效與資料報表 |
| `user` | 用戶 User | 個人頁面 | 僅限個人儀表板與資料查詢 |
| `guest` | 訪客 Guest | 訪客首頁 | 未登入或無對應群組，僅顯示公開資訊 |

角色由 Azure AD 群組對應決定（透過 `AZURE_GROUP_ROLE_MAP` 設定），優先等級為 admin > manager > user > guest。

---

## Azure DevOps 部署說明

專案內含 `azure-pipelines.yml`，包含兩個階段：

### 建置階段（Build）

- 安裝 Python 3.11
- 安裝 `requirements.txt` 中所有套件
- 驗證套件可正常匯入

### 部署階段（Deploy）

僅在推送至 `main` 分支時執行：

1. 使用 **qetza Replace Tokens** 任務，將 `.env.tokens` 中的 `#{VAR_NAME}#` 占位符替換為 Azure DevOps Pipeline 變數
2. 將 `.env.tokens` 複製為 `.env`
3. 部署至 Azure App Service（Linux），啟動指令為 `streamlit run app.py --server.port 8000 --server.address 0.0.0.0`

### 所需 Pipeline 變數

在 Azure DevOps Pipeline 設定中，需定義以下變數（建議設為機密）：

- `AZURE_CLIENT_ID`、`AZURE_CLIENT_SECRET`、`AZURE_TENANT_ID`
- `AZURE_REDIRECT_URI`、`AZURE_GROUP_ROLE_MAP`
- `ORACLE_HOST`、`ORACLE_PORT`、`ORACLE_SERVICE`、`ORACLE_USER`
- `ORACLE_PASSWORD_ENCRYPTED`、`FERNET_KEY`
- `APP_MODE`
- `AZURE_SUBSCRIPTION`（Azure 服務連線名稱）
- `AZURE_WEBAPP_NAME`（Azure App Service 名稱）

---

## 密碼加密說明

使用 `config.crypto` CLI 工具管理 Fernet 加密：

```bash
# 產生新的 Fernet 金鑰（首次設定時執行）
python -m config.crypto

# 加密資料庫密碼（需先設定 FERNET_KEY 環境變數）
python -m config.crypto encrypt <明文密碼>

# 解密確認（需先設定 FERNET_KEY 環境變數）
python -m config.crypto decrypt <密文>
```

將輸出的 `FERNET_KEY` 與 `ORACLE_PASSWORD_ENCRYPTED` 填入 `.env` 檔案。**請勿將 `.env` 提交至版本控制。**
