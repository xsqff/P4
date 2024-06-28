from flask import Blueprint, jsonify
from methods import methods

method_bp = Blueprint('methods', __name__, url_prefix='/methods')

@method_bp.route('', methods=['GET'])
def list_methods():
    return jsonify(methods), 200
