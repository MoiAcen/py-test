"""
應用程式設定模組 - 從環境變數載入所有設定項
"""
import os
from dotenv import load_dotenv

# 載入 .env 檔案（如果存在）
load_dotenv()


class Settings:
    """集中管理所有設定項"""

    # Azure Entra (Azure AD) 設定
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET: str = os.getenv("AZURE_CLIENT_SECRET", "")
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    AZURE_REDIRECT_URI: str = os.getenv("AZURE_REDIRECT_URI", "http://localhost:8501")
    AZURE_AUTHORITY: str = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"
    AZURE_SCOPES: list[str] = ["User.Read", "GroupMember.Read.All"]

    # Azure AD 群組到角色的對應（格式: group_id:role,...）
    AZURE_GROUP_ROLE_MAP_RAW: str = os.getenv("AZURE_GROUP_ROLE_MAP", "")

    # Oracle 資料庫設定
    ORACLE_HOST: str = os.getenv("ORACLE_HOST", "localhost")
    ORACLE_PORT: int = int(os.getenv("ORACLE_PORT", "1521"))
    ORACLE_SERVICE: str = os.getenv("ORACLE_SERVICE", "XEPDB1")
    ORACLE_USER: str = os.getenv("ORACLE_USER", "system")
    ORACLE_PASSWORD_ENCRYPTED: str = os.getenv("ORACLE_PASSWORD_ENCRYPTED", "")

    # Fernet 加密金鑰
    FERNET_KEY: str = os.getenv("FERNET_KEY", "")

    # 應用模式: "production" 使用真實 Entra 認證, "demo" 使用模擬登入
    # 安全預設為 production（fail-closed），本機開發需於 .env 明確設定 demo
    APP_MODE: str = os.getenv("APP_MODE", "production").lower()

    @classmethod
    def is_demo_mode(cls) -> bool:
        """是否為示範模式"""
        return cls.APP_MODE == "demo"

    @classmethod
    def get_group_role_map(cls) -> dict[str, str]:
        """解析群組到角色的對應字典"""
        mapping: dict[str, str] = {}
        raw = cls.AZURE_GROUP_ROLE_MAP_RAW.strip()
        if not raw:
            return mapping
        for pair in raw.split(","):
            pair = pair.strip()
            if ":" in pair:
                group_id, role = pair.split(":", 1)
                mapping[group_id.strip()] = role.strip()
        return mapping

    @classmethod
    def validate_production(cls) -> list[str]:
        """驗證生產模式必要設定，回傳缺少項目清單"""
        required = {
            "AZURE_CLIENT_ID": cls.AZURE_CLIENT_ID,
            "AZURE_CLIENT_SECRET": cls.AZURE_CLIENT_SECRET,
            "AZURE_TENANT_ID": cls.AZURE_TENANT_ID,
            "FERNET_KEY": cls.FERNET_KEY,
        }
        return [k for k, v in required.items() if not v]


# 全域單例
settings = Settings()
