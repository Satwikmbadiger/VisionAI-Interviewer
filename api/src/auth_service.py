from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User

def register_user_logic(data):
    if User.query.filter_by(email=data.get('email')).first():
        return {"message": "User already exists"}, 400

    hashed_pw = generate_password_hash(data.get('password'), method='pbkdf2:sha256')
    new_user = User(
        
        username=data.get('username'),
        email=data.get('email'),
        password=hashed_pw
    )
    db.session.add(new_user)
    db.session.commit()
    return {"message": "Registration successful"}, 201

def login_user_logic(data):
    user = User.query.filter_by(email=data.get('email')).first()
    if user and check_password_hash(user.password, data.get('password')):
       return {
            "message": "Login successful", 
            "userId": user.id, 
            "fullName": user.username
        }, 200
    return {"message": "Invalid credentials"}, 401