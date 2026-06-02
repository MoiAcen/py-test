"""
加密解密工具模組 - 基於 Fernet 對稱加密
用於安全儲存資料庫密碼等敏感資訊

CLI 用法:
    python -m config.crypto                    # 產生新的 Fernet 金鑰
    python -m config.crypto encrypt <明文>      # 加密字串
    python -m config.crypto decrypt <密文>      # 解密字串（需要設定 FERNET_KEY 環境變數）
"""
import base64
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


def _cli_main() -> None:
    """命令列入口"""
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

    if command == "encrypt" and len(args) >= 2:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("FERNET_KEY", "")
        if not key:
            print("錯誤: 請先設定環境變數 FERNET_KEY")
            sys.exit(1)
        plain = args[1]
        result = encrypt_password(plain, key)
        print(f"加密結果: {result}")

    elif command == "decrypt" and len(args) >= 2:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("FERNET_KEY", "")
        if not key:
            print("錯誤: 請先設定環境變數 FERNET_KEY")
            sys.exit(1)
        encrypted = args[1]
        result = decrypt_password(encrypted, key)
        print(f"解密結果: {result}")

    else:
        print("用法:")
        print("  python -m config.crypto                    # 產生新金鑰")
        print("  python -m config.crypto encrypt <明文>      # 加密")
        print("  python -m config.crypto decrypt <密文>      # 解密")


if __name__ == "__main__":
    _cli_main()
