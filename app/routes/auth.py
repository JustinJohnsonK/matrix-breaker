from flask import Blueprint
from controllers.auth_controller import get_profile, update_profile

# Auth routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api/user')

auth_bp.route('/profile', methods=['GET'])(get_profile)
auth_bp.route('/profile', methods=['PUT'])(update_profile)
