# Firebase Auth utility

import requests
import jwt
from flask import request, abort
from functools import wraps
import time
from app.utils.logger import get_logger

FIREBASE_PROJECT_ID = None
FIREBASE_CERTS_URL = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'

_cached_certs = None
_cached_certs_expiry = 0

logger = get_logger(__name__)


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
    logger.debug(f"JWT header: {header}")
    alg = header.get('alg')
    if alg != 'RS256':
        logger.error(f"JWT uses unsupported algorithm: {alg}")
        raise Exception(f'Unsupported JWT algorithm: {alg}')
    key_id = header['kid']
    cert = certs.get(key_id)
    if not cert:
        raise Exception('Invalid token: cert not found')
    if not isinstance(cert, str):
        logger.error(f"Cert for kid {key_id} is not a string: {type(cert)}")
        raise Exception('Cert is not a string')
    cert = cert.strip()
    logger.info(f"Cert for kid {key_id} length: {len(cert)}")
    logger.info(f"Cert for kid {key_id} start: {cert[:40]}")
    logger.info(f"Cert for kid {key_id} end: {cert[-40:]}")
    logger.info(f"Cert for kid {key_id} repr: {repr(cert)}")
    if not cert.startswith('-----BEGIN CERTIFICATE-----') or not cert.endswith('-----END CERTIFICATE-----'):
        logger.error(f"Cert for kid {key_id} does not have valid PEM markers.")
    try:
        decoded = jwt.decode(token, cert, algorithms=['RS256'], audience=project_id)
    except Exception as e:
        logger.error(f"JWT decode error: {e}")
        raise
    return decoded


def firebase_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if not auth or not auth.startswith('Bearer '):
            logger.warning('Missing or invalid Authorization header')
            abort(401, 'Missing or invalid Authorization header')
        token = auth.split(' ')[1]
        from config import load_config
        config = load_config()
        project_id = config['auth']['FIREBASE_PROJECT_ID']
        logger.info(f'Using Firebase project ID: {project_id}')
        try:
            decoded = verify_firebase_token(token, project_id)
            request.firebase_user = decoded
        except Exception as e:
            logger.error(f'Invalid token: {str(e)}')
            abort(401, f'Invalid token: {str(e)}')
        return f(*args, **kwargs)
    return decorated
