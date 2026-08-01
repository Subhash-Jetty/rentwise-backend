from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
import re
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS properly
    cors_origin = [
        origin.strip()
        for origin in os.environ.get("CORS_ORIGIN", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    cors_origin.extend([
        re.compile(r"^https://rentwise-frontend(?:-[a-z0-9]+)?-subhash-jettys-projects\.vercel\.app$"),
        "https://rentwise-frontend.vercel.app",
    ])
    CORS(
        app,
        resources={r"/*": {"origins": cors_origin}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )

    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.property_routes import property_bp
    from app.routes.analysis_routes import analysis_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(property_bp)
    app.register_blueprint(analysis_bp, url_prefix="/analysis")
   
    @app.route("/")
    def health_check():
       return "OK", 200

    with app.app_context():
        db.create_all()

    return app
