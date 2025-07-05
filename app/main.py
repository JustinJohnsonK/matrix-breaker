import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, jsonify
from config import load_config
from models.models import db, init_db
from routes.auth import auth_bp
from routes.ai import ai_bp
from routes.user import user_bp

# Main Flask app entrypoint

def create_app():
    app = Flask(__name__)
    config = load_config()
    app.config['SECRET_KEY'] = config['DEFAULT']['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = config['database']['DB_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        init_db()
    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(user_bp)
    @app.route('/ping')
    def ping():
        return jsonify({"ping": "pong"})
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
