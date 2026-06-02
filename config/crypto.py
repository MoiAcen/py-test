"""
加密解密工具模块 - 基于 Fernet 对称加密
用于安全存储数据库密码等敏感信息

CLI 用法:
    python -m config.crypto                    # 生成新的 Fernet 密钥
    python -m config.crypto encrypt <明文>      # 加密字符串
    python -m config.crypto decrypt <密文>      # 解密字符串（需要设置 FERNET_KEY 环境变量）
"""
import base64
import sys
from cryptography.fernet import Fernet


def generate_key() -> str:
    """生成一个新的 Fernet 密钥（Base64 URL 安全编码的 32 字节密钥）"""
    return Fernet.generate_key().decode("utf-8")


def encrypt_password(plain: str, key: str) -> str:
    """
    使用 Fernet 加密明文密码

    Args:
        plain: 明文字符串
        key:   Base64 编码的 Fernet 密钥

    Returns:
        Base64 编码的加密字符串
    """
    f = Fernet(key.encode("utf-8"))
    encrypted_bytes = f.encrypt(plain.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt_password(encrypted: str, key: str) -> str:
    """
    使用 Fernet 解密加密密码

    Args:
        encrypted: Base64 编码的加密字符串
        key:       Base64 编码的 Fernet 密钥

    Returns:
        解密后的明文字符串

    Raises:
        cryptography.fernet.InvalidToken: 密钥错误或数据被篡改
    """
    f = Fernet(key.encode("utf-8"))
    decrypted_bytes = f.decrypt(encrypted.encode("utf-8"))
    return decrypted_bytes.decode("utf-8")


def _cli_main() -> None:
    """命令行入口"""
    args = sys.argv[1:]

    if not args:
        # 默认：生成新密钥并展示使用示例
        new_key = generate_key()
        print("=" * 60)
        print("Fernet 密钥生成成功！")
        print("=" * 60)
        print(f"\nFERNET_KEY={new_key}")
        print("\n使用示例（加密密码）:")
        example_encrypted = encrypt_password("your_db_password", new_key)
        print(f"  明文: your_db_password")
        print(f"  密文: {example_encrypted}")
        print("\n将以下内容添加到 .env 文件:")
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
            print("错误: 请先设置环境变量 FERNET_KEY")
            sys.exit(1)
        plain = args[1]
        result = encrypt_password(plain, key)
        print(f"加密结果: {result}")

    elif command == "decrypt" and len(args) >= 2:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("FERNET_KEY", "")
        if not key:
            print("错误: 请先设置环境变量 FERNET_KEY")
            sys.exit(1)
        encrypted = args[1]
        result = decrypt_password(encrypted, key)
        print(f"解密结果: {result}")

    else:
        print("用法:")
        print("  python -m config.crypto                    # 生成新密钥")
        print("  python -m config.crypto encrypt <明文>      # 加密")
        print("  python -m config.crypto decrypt <密文>      # 解密")


if __name__ == "__main__":
    _cli_main()
