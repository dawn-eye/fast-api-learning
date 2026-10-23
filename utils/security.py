import bcrypt

def get_hash_password(password: str) -> str:
    # bcrypt 只处理前 72 字节，超长要先截断
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode()

#验证密码
def verify_password(plain_password,hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'),hashed_password.encode('utf-8'))