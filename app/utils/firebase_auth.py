# Firebase Auth utility

import requests
import jwt
from flask import request, abort
from functools import wraps
import time

FIREBASE_PROJECT_ID = None
FIREBASE_CERTS_URL = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'

_cached_certs = None
_cached_certs_expiry = 0


def get_firebase_certs():
    global _cached_certs, _cached_certs_expiry
    if _cached_certs and time.time() < _cached_certs_expiry:
        return _cached_certs
    resp = requests.get(FIREBASE_CERTS_URL)
    _cached_certs = resp.json()
    _cached_certs_expiry = time.time() + 3600
    return _cached_certs


def verify_firebase_token(token, project_id):
    certs = get_firebase_certs()
    header = jwt.get_unverified_header(token)
    key_id = header['kid']
    cert = certs.get(key_id)
    if not cert:
        raise Exception('Invalid token: cert not found')
    decoded = jwt.decode(token, cert, algorithms=['RS256'], audience=project_id)
    return decoded


def firebase_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if not auth or not auth.startswith('Bearer '):
            abort(401, 'Missing or invalid Authorization header')
        token = auth.split(' ')[1]
        from config import load_config
        config = load_config()
        project_id = config['auth']['FIREBASE_PROJECT_ID']
        try:
            decoded = verify_firebase_token(token, project_id)
            request.firebase_user = decoded
        except Exception as e:
            abort(401, f'Invalid token: {str(e)}')
        return f(*args, **kwargs)
    return decorated
