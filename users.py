from flask import Blueprint, request, jsonify
from models import db, User
from services.user_service import UserService

user_bp = Blueprint('users', __name__, url_prefix='/users')

@user_bp.route('', methods=['POST'])
def add_user():
    data = request.json
    response = UserService.add_user(data)
    return jsonify(response), response['status']

@user_bp.route('', methods=['GET'])
def list_users():
    response = UserService.list_users()
    return jsonify(response), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    response = UserService.delete_user(user_id)
    return jsonify(response), response['status']
