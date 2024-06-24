from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
from datetime import datetime

app = Flask(__name__)
api = Api(app)

ALPHABET = " ,.:(_)-0123456789АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
users = []
methods = [
    {"id": 1, "caption": "CAESAR", "json_params": '{"shift": "int"}', "description": "Caesar cipher"},
    {"id": 2, "caption": "VIGENERE", "json_params": '{"key": "string"}', "description": "Vigenere cipher"}
]
sessions = []
user_counter = 1
session_counter = 1


def caesar_cipher(text, shift, decrypt=False):
    result = []
    shift = -shift if decrypt else shift
    for char in text:
        if char in ALPHABET:
            idx = (ALPHABET.index(char) + shift) % len(ALPHABET)
            result.append(ALPHABET[idx])
        else:
            result.append(char)
    return ''.join(result)


def vigenere_cipher(text, key, decrypt=False):
    result = []
    key_indices = [ALPHABET.index(k) for k in key]
    key_length = len(key_indices)
    for i, char in enumerate(text):
        if char in ALPHABET:
            key_idx = key_indices[i % key_length]
            idx = (ALPHABET.index(char) + (-key_idx if decrypt else key_idx)) % len(ALPHABET)
            result.append(ALPHABET[idx])
        else:
            result.append(char)
    return ''.join(result)


class UserResource(Resource):
    def post(self):
        global user_counter
        data = request.get_json()
        new_user = {"id": user_counter, "login": data['login'], "secret": data['secret']}
        users.append(new_user)
        user_counter += 1
        return make_response(jsonify({"message": "User created successfully", "user": new_user}), 201)

    def get(self):
        result = [{"id": user['id'], "login": user['login']} for user in users]
        return make_response(jsonify(result), 200)


class MethodResource(Resource):
    def get(self):
        return make_response(jsonify(methods), 200)


class SessionResource(Resource):
    def post(self):
        global session_counter
        data = request.get_json()
        user_id = data['user_id']
        method_id = data['method_id']
        action = data.get('action', 'encrypt')
        user = next((u for u in users if u['id'] == user_id), None)
        method = next((m for m in methods if m['id'] == method_id), None)

        if not user:
            return make_response(jsonify({"message": "User not found"}), 404)
        if not method:
            return make_response(jsonify({"message": "Method not found"}), 404)

        data_in = data['data_in'].upper()
        data_in = ''.join(filter(lambda x: x in ALPHABET, data_in))
        params = data.get('params', {})
        start_time = datetime.now()

        if method['caption'] == "CAESAR":
            shift = int(params.get('shift', 0))
            data_out = caesar_cipher(data_in, shift, decrypt=(action == 'decrypt'))
        elif method['caption'] == "VIGENERE":
            key = params.get('key', '')
            data_out = vigenere_cipher(data_in, key, decrypt=(action == 'decrypt'))

        end_time = datetime.now()
        time_op = (end_time - start_time).total_seconds()

        new_session = {
            "id": session_counter,
            "user_id": user_id,
            "method_id": method_id,
            "data_in": data_in,
            "params": params,
            "data_out": data_out,
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "time_op": str(time_op)
        }
        sessions.append(new_session)
        session_counter += 1
        return make_response(jsonify({"message": "Encryption session created successfully", "session": new_session}), 201)

    def get(self, session_id):
        session = next((s for s in sessions if s['id'] == session_id), None)
        if not session:
            return make_response(jsonify({"message": "Session not found"}), 404)
        return make_response(jsonify(session), 200)

    def delete(self, session_id):
        data = request.get_json()
        session = next((s for s in sessions if s['id'] == session_id), None)
        if not session:
            return make_response(jsonify({"message": "Session not found"}), 404)
        user = next((u for u in users if u['id'] == session['user_id']), None)
        if user['secret'] != data['secret']:
            return make_response(jsonify({"message": "Unauthorized"}), 401)
        sessions.remove(session)
        return make_response(jsonify({"message": "Session deleted successfully"}), 200)


api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(MethodResource, '/methods')
api.add_resource(SessionResource, '/sessions', '/sessions/<int:session_id>')

if __name__ == '__main__':
    app.run(debug=True)
