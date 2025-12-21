from flask import Blueprint, request, jsonify
from auth_service import register_user_logic, login_user_logic
from dashboard_service import user_dashBoard_logic

# Using Blueprints for better organization
auth_bp = Blueprint('auth', __name__)
users_bp=Blueprint('users',__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    response, status = register_user_logic(request.json)
    return jsonify(response), status

@auth_bp.route('/login', methods=['POST'])
def login():
    response, status = login_user_logic(request.json)
    return jsonify(response), status

@users_bp.route('/<userId>', methods=['GET'])
def userDashBoard(userId):
    response,status= user_dashBoard_logic(int(userId))
    return jsonify(response),status