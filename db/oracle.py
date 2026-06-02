"""
Oracle 数据库连接模块

使用 oracledb thin 模式（无需 Oracle 客户端库）
密码通过 Fernet 解密后使用，避免明文存储
"""
import oracledb
from typing import Optional

from config.settings import settings
from config.crypto import decrypt_password


def get_connection() -> oracledb.Connection:
    """
    建立 Oracle 数据库连接

    密码从加密的环境变量中解密获取，使用 thin 模式连接。

    Returns:
        oracledb.Connection 连接对象

    Raises:
        ValueError: 配置缺失（未设置 FERNET_KEY 或加密密码）
        oracledb.Error: 数据库连接失败
    """
    if not settings.FERNET_KEY:
        raise ValueError(
            "FERNET_KEY 未配置。请运行 `python -m config.crypto` 生成密钥。"
        )
    if not settings.ORACLE_PASSWORD_ENCRYPTED:
        raise ValueError(
            "ORACLE_PASSWORD_ENCRYPTED 未配置。"
            "请运行 `python -m config.crypto encrypt <密码>` 加密数据库密码。"
        )

    # 解密数据库密码
    plain_password = decrypt_password(
        settings.ORACLE_PASSWORD_ENCRYPTED,
        settings.FERNET_KEY,
    )

    # 构建连接字符串（Easy Connect 格式）
    dsn = f"{settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.ORACLE_SERVICE}"

    # 使用 thin 模式（不依赖 Oracle 客户端）
    connection = oracledb.connect(
        user=settings.ORACLE_USER,
        password=plain_password,
        dsn=dsn,
    )
    return connection


def test_connection() -> tuple[bool, str]:
    """
    测试数据库连接是否正常

    执行 SELECT 1 FROM DUAL 验证连通性。

    Returns:
        (success: bool, message: str) 元组
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row and row[0] == 1:
            return (True, f"连接成功！Oracle @ {settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.ORACLE_SERVICE}")
        return (False, "查询返回异常结果")
    except ValueError as e:
        return (False, f"配置错误: {e}")
    except oracledb.Error as e:
        error_obj, = e.args
        return (False, f"Oracle 错误 [{error_obj.code}]: {error_obj.message}")
    except Exception as e:
        return (False, f"未知错误: {e}")


def execute_query(sql: str, params: Optional[dict] = None) -> tuple[list[str], list[tuple]]:
    """
    执行查询并返回列名和数据行

    Args:
        sql:    SQL 查询语句（使用 :param_name 占位符）
        params: 查询参数字典（可选）

    Returns:
        (columns, rows) 元组

    Raises:
        同 get_connection() 的异常
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or {})
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        return (columns, rows)
    finally:
        conn.close()
