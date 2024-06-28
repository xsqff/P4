from flask import Blueprint, request, jsonify
from services.session_service import SessionService

session_bp = Blueprint('sessions', __name__, url_prefix='/sessions')

@session_bp.route('', methods=['POST'])
def create_session():
    data = request.json
    response = SessionService.create_session(data)
    return jsonify(response), response['status']

@session_bp.route('', methods=['GET'])
def list_sessions():
    response = SessionService.list_sessions()
    return jsonify(response), 200

@session_bp.route('/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    data = request.json
    response = SessionService.delete_session(session_id, data)
    return jsonify(response), response['status']
