"""
应用配置模块 - 从环境变量加载所有配置项
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
load_dotenv()


class Settings:
    """集中管理所有配置项"""

    # Azure Entra (Azure AD) 配置
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET: str = os.getenv("AZURE_CLIENT_SECRET", "")
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    AZURE_REDIRECT_URI: str = os.getenv("AZURE_REDIRECT_URI", "http://localhost:8501")
    AZURE_AUTHORITY: str = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"
    AZURE_SCOPES: list[str] = ["User.Read", "GroupMember.Read.All"]

    # Azure AD 群组到角色的映射（格式: group_id:role,...）
    AZURE_GROUP_ROLE_MAP_RAW: str = os.getenv("AZURE_GROUP_ROLE_MAP", "")

    # Oracle 数据库配置
    ORACLE_HOST: str = os.getenv("ORACLE_HOST", "localhost")
    ORACLE_PORT: int = int(os.getenv("ORACLE_PORT", "1521"))
    ORACLE_SERVICE: str = os.getenv("ORACLE_SERVICE", "XEPDB1")
    ORACLE_USER: str = os.getenv("ORACLE_USER", "system")
    ORACLE_PASSWORD_ENCRYPTED: str = os.getenv("ORACLE_PASSWORD_ENCRYPTED", "")

    # Fernet 加密密钥
    FERNET_KEY: str = os.getenv("FERNET_KEY", "")

    # 应用模式: "production" 使用真实 Entra 认证, "demo" 使用模拟登录
    APP_MODE: str = os.getenv("APP_MODE", "demo").lower()

    @classmethod
    def is_demo_mode(cls) -> bool:
        """是否为演示模式"""
        return cls.APP_MODE == "demo"

    @classmethod
    def get_group_role_map(cls) -> dict[str, str]:
        """解析群组到角色的映射字典"""
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
        """验证生产模式必要配置，返回缺失项列表"""
        required = {
            "AZURE_CLIENT_ID": cls.AZURE_CLIENT_ID,
            "AZURE_CLIENT_SECRET": cls.AZURE_CLIENT_SECRET,
            "AZURE_TENANT_ID": cls.AZURE_TENANT_ID,
            "FERNET_KEY": cls.FERNET_KEY,
        }
        return [k for k, v in required.items() if not v]


# 全局单例
settings = Settings()
