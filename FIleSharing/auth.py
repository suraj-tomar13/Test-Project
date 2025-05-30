import base64

def simple_hash(pw: str):
    return base64.b64encode(pw.encode()).decode()

def simple_check(raw, hashed):
    return simple_hash(raw) == hashed

def create_token(user_id: int):
    return base64.b64encode(str(user_id).encode()).decode()

def get_user_id(token: str):
    try:
        return int(base64.b64decode(token.encode()).decode())
    except:
        return None
