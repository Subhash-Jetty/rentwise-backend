from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS properly
    CORS(
        app,
        resources={r"/*": {"origins": "https://rentwise-frontend-two.vercel.app"}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )

    db.init_app(app)
    jwt.init_app(app)

    # Upload folder setup
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Serve uploaded images
    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.property_routes import property_bp
    from app.routes.analysis_routes import analysis_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(property_bp)
    app.register_blueprint(analysis_bp, url_prefix="/analysis")

    with app.app_context():
        db.create_all()

    return app