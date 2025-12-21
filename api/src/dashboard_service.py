from database import db
from models import User
from models import Stats

def user_dashBoard_logic(data):
    print(data)
    user = User.query.filter_by(id=data).first()
    return {"username":user.username},200
    
    