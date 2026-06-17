"""
Oracle 資料庫連線模組

使用 oracledb thin 模式（無需 Oracle 用戶端程式庫）
密碼透過 Fernet 解密後使用，避免明文儲存
"""
import oracledb
from typing import Optional

from config.settings import settings
from config.crypto import decrypt_password


def get_connection() -> oracledb.Connection:
    """
    建立 Oracle 資料庫連線

    密碼從加密的環境變數中解密取得，使用 thin 模式連線。

    Returns:
        oracledb.Connection 連線物件

    Raises:
        ValueError: 設定缺少（未設定 FERNET_KEY 或加密密碼）
        oracledb.Error: 資料庫連線失敗
    """
    if not settings.FERNET_KEY:
        raise ValueError(
            "FERNET_KEY 未設定。請執行 `python -m config.crypto` 產生金鑰。"
        )
    if not settings.ORACLE_PASSWORD_ENCRYPTED:
        raise ValueError(
            "ORACLE_PASSWORD_ENCRYPTED 未設定。"
            "請執行 `python -m config.crypto encrypt <密碼>` 加密資料庫密碼。"
        )

    # 解密資料庫密碼
    plain_password = decrypt_password(
        settings.ORACLE_PASSWORD_ENCRYPTED,
        settings.FERNET_KEY,
    )

    # 建立連線字串（Easy Connect 格式）
    dsn = f"{settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.ORACLE_SERVICE}"

    # 使用 thin 模式（不依賴 Oracle 用戶端）
    connection = oracledb.connect(
        user=settings.ORACLE_USER,
        password=plain_password,
        dsn=dsn,
    )
    return connection


def test_connection() -> tuple[bool, str]:
    """
    測試資料庫連線是否正常

    執行 SELECT 1 FROM DUAL 驗證連線狀態。

    Returns:
        (success: bool, message: str) 元組
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row and row[0] == 1:
            return (True, f"連線成功！Oracle @ {settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.ORACLE_SERVICE}")
        return (False, "查詢回傳異常結果")
    except ValueError as e:
        return (False, f"設定錯誤: {e}")
    except oracledb.Error as e:
        # 防禦性處理：部分 oracledb.Error 的 args 未必恰好一個元素
        error_obj = e.args[0] if e.args else None
        if error_obj is not None and hasattr(error_obj, "code"):
            return (False, f"Oracle 錯誤 [{error_obj.code}]: {error_obj.message}")
        return (False, f"Oracle 錯誤: {e}")
    except Exception as e:
        return (False, f"未知錯誤: {e}")


def execute_query(sql: str, params: Optional[dict] = None) -> tuple[list[str], list[tuple]]:
    """
    執行查詢並回傳欄位名稱和資料列

    Args:
        sql:    SQL 查詢語句（使用 :param_name 占位符）
        params: 查詢參數字典（可選）

    Returns:
        (columns, rows) 元組

    Raises:
        同 get_connection() 的例外
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
