#create & verify tokens
import jwt, os
import datetime
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('JWT_SECRET_KEY')

if not SECRET_KEY:
    raise RuntimeError('JWT_SECRET_KEY not set in envirnment')

def generate_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role.upper(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token):
    try: 
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise Exception('Token expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')