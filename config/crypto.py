"""
加密解密工具模組 - 基於 Fernet 對稱加密
用於安全儲存資料庫密碼等敏感資訊

CLI 用法:
    python -m config.crypto                    # 產生新的 Fernet 金鑰
    python -m config.crypto encrypt <明文>      # 加密字串
    python -m config.crypto decrypt <密文>      # 解密字串（需要設定 FERNET_KEY 環境變數）
"""
import sys
from cryptography.fernet import Fernet


def generate_key() -> str:
    """產生一個新的 Fernet 金鑰（Base64 URL 安全編碼的 32 位元組金鑰）"""
    return Fernet.generate_key().decode("utf-8")


def encrypt_password(plain: str, key: str) -> str:
    """
    使用 Fernet 加密明文密碼

    Args:
        plain: 明文字串
        key:   Base64 編碼的 Fernet 金鑰

    Returns:
        Base64 編碼的加密字串
    """
    f = Fernet(key.encode("utf-8"))
    encrypted_bytes = f.encrypt(plain.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt_password(encrypted: str, key: str) -> str:
    """
    使用 Fernet 解密加密密碼

    Args:
        encrypted: Base64 編碼的加密字串
        key:       Base64 編碼的 Fernet 金鑰

    Returns:
        解密後的明文字串

    Raises:
        cryptography.fernet.InvalidToken: 金鑰錯誤或資料遭竄改
    """
    f = Fernet(key.encode("utf-8"))
    decrypted_bytes = f.decrypt(encrypted.encode("utf-8"))
    return decrypted_bytes.decode("utf-8")


def _load_key() -> str:
    """從 .env / 環境變數載入 FERNET_KEY，缺少時結束程式"""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("FERNET_KEY", "")
    if not key:
        # 提示訊息輸出至 stderr，保持 stdout 乾淨（供腳本擷取）
        print("錯誤: 請先設定環境變數 FERNET_KEY", file=sys.stderr)
        sys.exit(1)
    return key


def _read_value(args: list[str], prompt_label: str) -> str:
    """取得待處理字串：優先用 argv，否則自 stdin 讀取（避免敏感值出現在 process 清單）"""
    if len(args) >= 2:
        return args[1]
    # 從 stdin 讀取（可由腳本以 pipe 傳入隱藏輸入）
    print(f"請輸入{prompt_label}（由 stdin 讀取）:", file=sys.stderr)
    return sys.stdin.readline().rstrip("\n")


def _cli_main() -> None:
    """
    命令列入口

    設計原則：encrypt/decrypt 的結果以「純文字」輸出至 stdout，
    所有提示訊息輸出至 stderr，方便 shell 腳本直接擷取結果。
    """
    args = sys.argv[1:]

    if not args:
        # 預設：產生新金鑰並展示使用範例
        new_key = generate_key()
        print("=" * 60)
        print("Fernet 金鑰產生成功！")
        print("=" * 60)
        print(f"\nFERNET_KEY={new_key}")
        print("\n使用範例（加密密碼）:")
        example_encrypted = encrypt_password("your_db_password", new_key)
        print(f"  明文: your_db_password")
        print(f"  密文: {example_encrypted}")
        print("\n將以下內容新增至 .env 檔案:")
        print(f"  FERNET_KEY={new_key}")
        print(f"  ORACLE_PASSWORD_ENCRYPTED={example_encrypted}")
        return

    command = args[0].lower()

    if command == "encrypt":
        key = _load_key()
        plain = _read_value(args, "要加密的明文")
        print(encrypt_password(plain, key))

    elif command == "decrypt":
        key = _load_key()
        encrypted = _read_value(args, "要解密的密文")
        print(decrypt_password(encrypted, key))

    else:
        print("用法:", file=sys.stderr)
        print("  python -m config.crypto                    # 產生新金鑰", file=sys.stderr)
        print("  python -m config.crypto encrypt <明文>      # 加密（亦可由 stdin 傳入）", file=sys.stderr)
        print("  python -m config.crypto decrypt <密文>      # 解密（亦可由 stdin 傳入）", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _cli_main()
