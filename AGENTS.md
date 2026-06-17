# AGENTS.md

本文件提供給後續接手的 AI 代理（與開發者），協助快速理解專案結構、慣例與注意事項。

---

## 專案概述

**企業資料平台** — 一個以 Streamlit 建構的內部資料平台，整合：

- **Azure Entra ID（Azure AD）** 單一登入（MSAL OAuth2 授權碼流程）
- **角色型存取控制（RBAC）**：`admin` / `manager` / `user` / `guest`
- **Oracle 資料庫**連線（oracledb thin 模式，密碼以 Fernet 加密儲存）
- **Demo 示範模式**：無需真實 Azure AD，可直接切換角色測試
- 部署目標為 **Azure DevOps Pipeline + Azure App Service**，採用 **Replace Tokens** 注入環境變數

---

## 目錄結構

```
py-test/
├── app.py                  # Streamlit 主入口（OAuth 回呼處理、路由、側邊欄）
├── requirements.txt        # Python 相依套件
├── azure-pipelines.yml     # Azure DevOps CI/CD（Build + Deploy 兩階段）
├── startup.sh / startup.bat        # 啟動腳本（Linux / Windows）
├── keygen.sh  / keygen.bat         # 金鑰產生與密碼加解密工具
├── verify_db / verify_entra / verify_all (.sh/.bat)  # 驗證腳本（薄包裝）
├── .env.example            # 環境變數說明範本（本機開發用）
├── .env.tokens             # Replace Tokens 部署範本（含 #{VAR}# 占位符）
├── Vault.md                # Azure Key Vault 金鑰管理改進建議
├── config/
│   ├── settings.py         # 集中管理所有設定（從環境變數讀取）
│   └── crypto.py           # Fernet 加解密工具 + CLI
├── auth/
│   ├── entra.py            # MSAL 認證流程 + Demo 模擬用戶
│   └── roles.py            # 角色權限定義、群組→角色對應
├── db/
│   └── oracle.py           # Oracle 連線、test_connection、execute_query
├── utils/
│   └── session.py          # Streamlit Session State 封裝
├── views/                  # 各角色頁面（※ 不可命名為 pages/，見下方注意事項）
│   ├── admin.py            # 管理員控制台
│   ├── manager.py          # 經理儀表板
│   ├── user.py             # 個人儀表板
│   └── guest.py            # 訪客首頁
└── scripts/
    ├── verify_db.py        # Oracle 連線驗證邏輯
    ├── verify_entra.py     # Entra 登入驗證邏輯（含互動式登入）
    └── verify_all.py       # 完整系統驗證（整合上述）
```

---

## 重要慣例（請務必遵守）

### 1. 語言
- **所有面向使用者的文字、註解、docstring 一律使用繁體中文**，禁止出現簡體字。
- 變數、函式、類別名稱維持英文。

### 2. 目錄命名 — 不可使用 `pages/`
- Streamlit 會自動將根目錄下的 `pages/` 視為**多頁應用程式**並產生導航。
- 本專案角色頁面放在 **`views/`**，路由由 `app.py` 依角色手動分派（`_render_main_content`）。
- 新增角色頁面請放 `views/`，並在 `app.py` 的路由與側邊欄 `nav_items` 補上對應。

### 3. 安全預設 — fail-closed
- `APP_MODE` 預設為 **`production`**（`config/settings.py`）。未設定時不會落入 demo。
- **Demo 模式允許任意選角色登入，僅供本機開發，嚴禁用於正式環境。**
- OAuth CSRF state 驗證為 fail-closed：缺少 saved_state 即拒絕（`app.py:_handle_oauth_callback`）。

### 4. 密碼與金鑰
- 資料庫密碼**絕不明文儲存**，一律經 Fernet 加密後放 `ORACLE_PASSWORD_ENCRYPTED`。
- 金鑰 `FERNET_KEY` 透過 `python-dotenv` 自 `.env` 載入；**不要在 shell/bat 手動 export**（已知會因特殊字元解析失敗）。
- `config/crypto.py` 的 CLI **以純文字輸出至 stdout、提示訊息至 stderr**，方便腳本擷取。修改時務必維持此分離。
- `.env` 已列入 `.gitignore`，**永遠不要提交真實密鑰**。`.env.tokens`（占位符）則需追蹤。

---

## 常用指令

```bash
# 安裝相依套件
pip install -r requirements.txt

# 產生 Fernet 金鑰 / 加解密密碼
python -m config.crypto                 # 產生新金鑰
python -m config.crypto encrypt <明文>   # 加密（亦可由 stdin 傳入）
python -m config.crypto decrypt <密文>   # 解密
bash keygen.sh encrypt                   # 互動式（密碼隱藏輸入）

# 啟動應用程式
streamlit run app.py                     # 跨平台
bash startup.sh                          # Linux
startup.bat                              # Windows

# 驗證
bash verify_db.sh                        # 僅驗證 Oracle
bash verify_entra.sh                     # 僅驗證 Entra 登入
bash verify_all.sh                       # 完整驗證

# 語法檢查（CI 亦執行此項）
python -m compileall -q app.py config auth db utils views scripts
```

---

## 環境變數

| 變數 | 用途 | 備註 |
|------|------|------|
| `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` / `AZURE_TENANT_ID` | Azure AD 應用程式憑證 | production 必填 |
| `AZURE_REDIRECT_URI` | OAuth2 回呼 URI | 需於 Azure AD 註冊 |
| `AZURE_GROUP_ROLE_MAP` | 群組 ID→角色對應 | 格式 `gid1:admin,gid2:manager` |
| `ORACLE_HOST` / `ORACLE_PORT` / `ORACLE_SERVICE` / `ORACLE_USER` | Oracle 連線 | |
| `ORACLE_PASSWORD_ENCRYPTED` | Fernet 加密後的密碼 | 由 `config.crypto` 產生 |
| `FERNET_KEY` | Fernet 對稱金鑰 | 機密，建議改用 Key Vault（見 Vault.md） |
| `APP_MODE` | `demo` 或 `production` | 預設 production |

---

## 部署（Azure DevOps）

`azure-pipelines.yml` 兩階段：

1. **Build**：安裝套件 → 驗證匯入 → `compileall` 語法檢查
2. **Deploy**（僅 `main`）：
   - `qetza.replacetokens@6` 將 `.env.tokens` 的 `#{VAR}#` 替換為 Pipeline 變數
   - `cp .env.tokens .env`
   - `AzureWebApp@1` 部署至 App Service

**Pipeline 變數**（機密請設為 Secret）：所有上表環境變數 + `AZURE_SUBSCRIPTION`、`AZURE_WEBAPP_NAME`。

---

## 開發流程（給接手的 AI）

1. **分支**：在指定的功能分支開發，例如 `claude/inspiring-babbage-CIjfR`，勿直接推 `main`。
2. **修改後驗證**：至少跑 `python -m compileall ...`；若有安裝套件，跑對應 `verify_*` 腳本。
3. **提交訊息**：使用繁體中文、具描述性（例：`fix: 修正 CSRF 驗證 fail-closed`）。
4. **推送**：`git push -u origin <branch>`，失敗時以指數退避重試。
5. **勿建立 PR**，除非使用者明確要求。

---

## 已知技術債 / 後續改進方向

- **金鑰管理**：目前 `FERNET_KEY` 與密文同存於環境變數，任一外洩即可解密。建議導入 **Azure Key Vault + Managed Identity**，詳見 [`Vault.md`](./Vault.md)。
- **Session 延續性**：production 的 OAuth 跳轉使用 `<meta refresh>`，需實測 Streamlit session 在跳轉後是否保留 `oauth_state`（影響 CSRF 驗證流程）。
- **Token 過期/更新**：目前登入後 session 持續，未處理 access token 過期與 refresh。
- **頁面資料**：`views/` 各頁目前為模擬資料（mock），尚未接上真實 Oracle 查詢。
- **CI 測試**：Build 階段僅做語法檢查，無單元測試；可加入 `pytest`（注意需 mock Azure/Oracle）。

### Entra 互動式登入驗證的前置設定

`scripts/verify_entra.py` 的互動式登入使用本機回呼 `http://localhost:8502`。
執行前必須在 Azure AD 應用程式的 **「驗證 → 重新導向 URI」** 中註冊
`http://localhost:8502`，否則 Azure 會以 `redirect_uri_mismatch` 拒絕登入。

### 範本擴充點標記

本專案為框架範本，程式中以下列標記標示「留給接手者實作」的位置，搜尋即可定位：

- `【範本擴充點】` — placeholder 函式 / 欄位（如 `views/*` 的 `_MOCK_*`、`_mock_*`，日期查詢欄位）
- `【範本說明】` — 刻意保留的示範行為說明（如 `views/user.py` 的固定模擬資料）

接手時請將這些 placeholder 替換為真實的 `db.oracle.execute_query(...)` 查詢或 Graph API 呼叫。

---

## 技術棧版本

- Python >= 3.11
- Streamlit >= 1.35、msal >= 1.28、oracledb >= 2.3、cryptography >= 42、pandas >= 2.0
- 完整清單見 `requirements.txt`
