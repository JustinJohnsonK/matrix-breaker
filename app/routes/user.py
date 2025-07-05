from flask import Blueprint
from controllers.user_controller import submit_review

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

user_bp.route('/review', methods=['POST'])(submit_review)

# User routes
