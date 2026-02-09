import unittest
import os
from app import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config.config import Config
from flask_cors import CORS 

def create_test_app():
    """Factory para crear app de testing con SQLite"""
    app = Flask(__name__, instance_relative_config=False)
    
    # Override config with test configuration
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    db.init_app(app)
    CORS(app)

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
        
        # Create test user for authentication
        from app.models.user import User
        
        test_user = User(
            external_id='test-user-id',
            firstName='Test',
            lastName='User',
            dni='12345678',
            email='dev@kallpa.com',
            password='xxxxx',
            role='Administrador',
            status='activo'
        )
        db.session.add(test_user)
        db.session.commit()
        
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
    
    return app


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        # Create test app with SQLite configuration
        self.app = create_test_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.app_context.pop()
