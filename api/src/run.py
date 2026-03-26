from flask import Flask
from flask_cors import CORS
from config import Config
from database import db
from routes import auth_bp,users_bp,interview_bp,health_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize DB
    db.init_app(app)

    # Enable CORS for React (port 3000/5173)
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"], supports_credentials=True)

    # Register the routes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(interview_bp, url_prefix='/api/interview')
    app.register_blueprint(health_bp, url_prefix='/api/')
    

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8080)