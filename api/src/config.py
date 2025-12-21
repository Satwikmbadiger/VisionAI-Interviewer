import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aceview_super_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False