import jwt, datetime
from django.utils import timezone
from django.conf import settings
from .models import MyUser

def validate_token(token):
    try:
        return jwt.decode(token, settings.SIGNATURE, algorithms=["HS256"])
    except Exception as e:
        return None

def generate_token(payload):
    payload['exp'] = datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(seconds=settings.TOKEN_EXPIRE_TIME)
    payload['iat'] = datetime.datetime.now(tz=timezone.utc) 
    return jwt.encode(payload, settings.SIGNATURE, algorithm='HS256')

def staff_perm(token):
    enc_info = validate_token(token)

    if enc_info:
        user = MyUser.objects.get(phone=enc_info.get('phone'))
        return user.user_category == 'Staff'

    return False