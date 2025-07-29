# dashboard/security.py
import os
import base64
from typing import Optional # <-- 修正: 添加导入
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext

# --- Password Hashing ---
# 使用 passlib 来安全地处理密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Encryption Key Derivation ---
# 这个盐是固定的, 用于从主密码派生加密密钥. 它不需要保密.
ENCRYPTION_SALT = b'eops-panel-encryption-salt'
# Fernet 要求密钥是 URL-safe base64编码的32字节.
KDF_ITERATIONS = 480000  # PBKDF2 推荐的迭代次数

# 全局的 Fernet 实例, 将在应用启动时被初始化
fernet: Optional[Fernet] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否与哈希值匹配"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """计算密码的哈希值"""
    return pwd_context.hash(password)

def derive_encryption_key(master_password: str) -> bytes:
    """从主密码派生出用于 Fernet 对称加密的密钥."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=ENCRYPTION_SALT,
        iterations=KDF_ITERATIONS,
    )
    # 使用主密码的 utf-8 编码作为 kdf 的输入
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key

def initialize_fernet(master_password: str):
    """
    使用主密码初始化全局的 Fernet 实例.
    这个函数应该在应用启动时, 在获取到主密码后调用.
    """
    global fernet
    encryption_key = derive_encryption_key(master_password)
    fernet = Fernet(encryption_key)

def encrypt_data(data: str) -> str:
    """使用 Fernet 加密字符串数据"""
    if not fernet:
        raise RuntimeError("Fernet has not been initialized. Call initialize_fernet() first.")
    if not data:
        return ""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """使用 Fernet 解密字符串数据"""
    if not fernet:
        raise RuntimeError("Fernet has not been initialized. Call initialize_fernet() first.")
    if not encrypted_data:
        return ""
    try:
        return fernet.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        return f"DECRYPTION_ERROR: {e}"