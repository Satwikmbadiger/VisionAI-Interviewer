from flask import Blueprint, request, jsonify
from auth_service import register_user_logic, login_user_logic
from dashboard_service import user_dashBoard_logic
from interviewSetup import generate_questions_logic, get_session_logic, ollama_health_logic
from HealthService import get_health

auth_bp      = Blueprint('auth', __name__)
users_bp     = Blueprint('users', __name__)
interview_bp = Blueprint('interview', __name__)
health_bp = Blueprint('health',__name__)




# ─── Auth ─────────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    response, status = register_user_logic(request.json)
    return jsonify(response), status


@auth_bp.route('/login', methods=['POST'])
def login():
    response, status = login_user_logic(request.json)
    return jsonify(response), status


# ─── Users ────────────────────────────────────────────────────────────────────

@users_bp.route('/<userId>', methods=['GET'])
def userDashBoard(userId):
    response, status = user_dashBoard_logic(int(userId))
    return jsonify(response), status


# ─── Interview ────────────────────────────────────────────────────────────────

@interview_bp.route('/generate-questions', methods=['POST'])
def generateQuestions():
    response, status = generate_questions_logic(
        raw_settings    = request.form.get("settings", "{}"),
        document_choice = request.form.get("document_choice", "both"),
        files           = request.files,         # ← pass the uploaded files
    )
    return jsonify(response), status


@interview_bp.route('/session/<session_id>', methods=['GET'])
def getSession(session_id):
    response, status = get_session_logic(session_id)
    return jsonify(response), status


@interview_bp.route('/ollama-health', methods=['GET'])
def ollamaHealth():
    response, status = ollama_health_logic()
    return jsonify(response), status

@health_bp.route('/health',methods=['GET'])
def getHealth():
    response,status=get_health()
    return jsonify(response), status
 