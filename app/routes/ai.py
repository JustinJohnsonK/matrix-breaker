from flask import Blueprint
from controllers.ai_controller import proofread, modify

ai_bp = Blueprint('ai', __name__, url_prefix='/api')

ai_bp.route('/proof-read', methods=['POST'])(proofread)
ai_bp.route('/modify', methods=['POST'])(modify)
