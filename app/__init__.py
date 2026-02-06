from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from app.config.config import Config
from flask_cors import CORS 

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    db.init_app(app)
    CORS(
        app, 
        resources={r"/*": {"origins": [
            "https://kallpa-frontend-app-fqcgcebxc5f5a6gg.westus3-01.azurewebsites.net",
            "http://localhost:3000", 
            "http://localhost:4200", 
            "http://localhost:3001", 
            "http://localhost:8080"
        ]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            return "", 200
    
    with app.app_context():
        from app import models
        db.create_all()
        
        # register blueprints
        from app.routes.user_routes import user_bp
        app.register_blueprint(user_bp, url_prefix='/api')
        from app.routes.attendance_routes import attendance_bp
        app.register_blueprint(attendance_bp, url_prefix='/api')
        from app.routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api')
        from app.routes.assessment_routes import assessment_bp
        app.register_blueprint(assessment_bp, url_prefix='/api')
        from app.routes.evaluation_routes import evaluation_bp
        app.register_blueprint(evaluation_bp, url_prefix='/api')
        
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
    
    return app
