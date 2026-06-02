# 金鑰管理改進建議

本文件說明目前密碼加密機制的限制，以及導入 Azure Key Vault 的改進方向。

---

## 目前實作的限制

目前 Fernet 金鑰與加密密文皆儲存於 `.env` / Pipeline Variables：

```
FERNET_KEY=abc123...               ← 金鑰
ORACLE_PASSWORD_ENCRYPTED=gAA...   ← 密文
```

**風險：** 兩者位於同一儲存位置，任一來源外洩即可完整還原明文密碼。

---

## 建議改進：Azure Key Vault

將 `FERNET_KEY` 移入 Azure Key Vault，應用程式執行期動態取得，金鑰不落地於任何設定檔。

### 架構對比

```
目前架構
─────────────────────────────────────────
.env / Pipeline Variables
  ├── FERNET_KEY          ← 金鑰明文
  └── ORACLE_PASSWORD_ENCRYPTED
              ↓
         decrypt()  →  DB 密碼


改進架構
─────────────────────────────────────────
.env / Pipeline Variables
  └── ORACLE_PASSWORD_ENCRYPTED   ← 僅密文

Azure Key Vault
  └── FERNET-KEY          ← 金鑰（受 IAM 控管）
              ↓ (執行期取得)
         decrypt()  →  DB 密碼
```

---

## 實作步驟

### 1. 建立 Key Vault 並上傳金鑰

```bash
# 建立 Key Vault
az keyvault create \
  --name <your-keyvault-name> \
  --resource-group <your-rg> \
  --location eastasia

# 上傳 Fernet 金鑰
az keyvault secret set \
  --vault-name <your-keyvault-name> \
  --name "FERNET-KEY" \
  --value "<your-fernet-key>"
```

### 2. 授權應用程式存取

```bash
# 取得 App Service 的受控識別 (Managed Identity) 物件 ID
az webapp identity assign \
  --name <app-name> \
  --resource-group <your-rg>

# 授予 Key Vault 讀取權限
az keyvault set-policy \
  --name <your-keyvault-name> \
  --object-id <managed-identity-object-id> \
  --secret-permissions get
```

### 3. 新增相依套件

```
azure-keyvault-secrets>=4.8.0
azure-identity>=1.17.0
```

### 4. 修改 config/crypto.py（建議改法）

```python
import os
from cryptography.fernet import Fernet

def _get_fernet_key() -> str:
    """
    依環境取得 Fernet 金鑰：
    - 設定 KEY_VAULT_URI 時從 Azure Key Vault 取得（生產環境）
    - 否則從環境變數 FERNET_KEY 取得（本機開發 / Demo）
    """
    vault_uri = os.getenv("KEY_VAULT_URI")
    if vault_uri:
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential
        client = SecretClient(vault_url=vault_uri, credential=DefaultAzureCredential())
        return client.get_secret("FERNET-KEY").value
    return os.getenv("FERNET_KEY", "")


def decrypt_password(encrypted: str, key: str = "") -> str:
    resolved_key = key or _get_fernet_key()
    return Fernet(resolved_key.encode()).decrypt(encrypted.encode()).decode()
```

### 5. 更新 .env.tokens

```bash
# 生產環境改用 Key Vault URI，移除 FERNET_KEY
KEY_VAULT_URI=#{KEY_VAULT_URI}#
ORACLE_PASSWORD_ENCRYPTED=#{ORACLE_PASSWORD_ENCRYPTED}#

# 本機開發仍可保留（Key Vault 不可用時的 fallback）
# FERNET_KEY=#{FERNET_KEY}#
```

---

## Azure DevOps Pipeline 對應調整

```yaml
# azure-pipelines.yml 新增步驟
- task: AzureKeyVault@2
  displayName: '從 Key Vault 讀取機密'
  inputs:
    azureSubscription: '$(AZURE_SUBSCRIPTION)'
    KeyVaultName: '$(KEY_VAULT_NAME)'
    SecretsFilter: 'FERNET-KEY'
    RunAsPreJob: true
```

取得後 `FERNET-KEY` 自動成為 Pipeline 變數，Replace Tokens 可直接注入（若仍需落地），或直接透過 `KEY_VAULT_URI` 讓應用程式執行期動態取得（建議）。

---

## 安全等級比較

| 方式 | 金鑰位置 | 風險等級 | 適用場景 |
|------|---------|---------|---------|
| 目前：`.env` 同存 | 設定檔 | 🔴 高 | 本機開發 |
| Pipeline Variables Secret | CI/CD 變數 | 🟡 中 | 無 Key Vault 時的過渡方案 |
| Azure Key Vault + Managed Identity | Key Vault | 🟢 低 | 生產環境建議方案 |
| Key Vault + 無密文（直接存 DB 密碼原文於 Vault） | Key Vault | 🟢 低 | 最簡化方案，移除 Fernet 層 |

---

## 備註

- 本機開發維持 `.env` + `FERNET_KEY` 方式，不影響現有 Demo 模式
- `KEY_VAULT_URI` 存在時自動切換為 Key Vault 模式，兩種環境共用同一份程式碼
- Managed Identity 不需要任何密碼或憑證，為 Azure 原生零信任方案
