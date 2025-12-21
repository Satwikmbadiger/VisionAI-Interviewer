from flask import Blueprint, request, jsonify
from auth_service import register_user_logic, login_user_logic

# Using Blueprints for better organization
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    response, status = register_user_logic(request.json)
    return jsonify(response), status

@auth_bp.route('/login', methods=['POST'])
def login():
    response, status = login_user_logic(request.json)
    return jsonify(response), status

# @app.route('/api/dashboard-stats', methods=['GET'])
# def userDashBoard():
#     response,status= user_dashBoard_logic()
#     return jsonify(response),status