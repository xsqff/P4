from flask import Blueprint, request, jsonify
from services.encryption_service import break_shift_cipher_wrapper

break_cipher_bp = Blueprint('break_cipher', __name__, url_prefix='/break')

@break_cipher_bp.route('', methods=['POST'])
def break_cipher():
    data = request.json
    response = break_shift_cipher_wrapper(data)
    return jsonify(response), response['status']
