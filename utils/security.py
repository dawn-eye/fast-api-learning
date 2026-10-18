import bcrypt

def get_hash_password(password: str) -> str:
    # bcrypt 只处理前 72 字节，超长要先截断
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8")[:72], hashed.encode("utf-8"))