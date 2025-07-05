# User controller logic

from flask import request, jsonify, abort
from models.models import db, User, Review, RateLimitLog
from utils.firebase_auth import firebase_auth_required
from datetime import datetime, timedelta
from config import load_config

def check_review_limit(user_id):
    today = datetime.utcnow().date()
    review = Review.query.filter(
        Review.user_id == user_id,
        db.func.date(Review.created_at) == today
    ).first()
    return review is not None

@firebase_auth_required
def submit_review():
    user_info = request.firebase_user
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        abort(404, 'User not found')
    if check_review_limit(user.id):
        abort(429, 'Only one review per day allowed')
    data = request.get_json()
    captcha = data.get('captcha', '')
    if captcha.lower() != 'cat':
        abort(400, 'Captcha failed')
    review = Review(
        user_id=user.id,
        review_text=data.get('review_text', ''),
        rating=int(data.get('rating', 5)),
        created_at=datetime.utcnow()
    )
    db.session.add(review)
    db.session.commit()
    # Log rate limit
    log = RateLimitLog(user_id=user.id, endpoint='/api/user/review', timestamp=datetime.utcnow())
    db.session.add(log)
    db.session.commit()
    return jsonify({'success': True, 'review_id': review.id})
