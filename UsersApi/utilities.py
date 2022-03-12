import jwt

def validate_token(token):
    try:
        return jwt.decode(token, "secret", algorithm="HS256")
    except:
        return None