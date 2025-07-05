# Auth controller logic

from flask import request, jsonify, abort
from models.models import db, User
from utils.firebase_auth import firebase_auth_required
from datetime import datetime

@firebase_auth_required
def get_profile():
    user_info = request.firebase_user
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(email=user_info['email'], name=user_info.get('name', ''), created_at=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
    return jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'created_at': user.created_at.isoformat()
    })

@firebase_auth_required
def update_profile():
    user_info = request.firebase_user
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        abort(404, 'User not found')
    data = request.get_json()
    user.name = data.get('name', user.name)
    db.session.commit()
    return jsonify({'success': True, 'name': user.name})
