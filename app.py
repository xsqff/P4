from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from datetime import datetime

# Инициализация приложения Flask и API
app = Flask(__name__)
api = Api(app)

# Определение алфавита для шифрования
ALPHABET = " ,.:(_)-0123456789AБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

# Временное хранилище данных
users = []
methods = [
    {"id": 1, "caption": "CAESAR", "json_params": '{"shift": "int"}', "description": "Caesar cipher"},
    {"id": 2, "caption": "VIGENERE", "json_params": '{"key": "string"}', "description": "Vigenere cipher"}
]
sessions = []
user_counter = 1
session_counter = 1


# Функция для шифрования методом Цезаря
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


# Функция для шифрования методом Виженера
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


# Ресурс для управления пользователями
class UserResource(Resource):
    def post(self):
        global user_counter
        data = request.get_json()
        new_user = {
            "id": user_counter,
            "login": data['login'],
            "secret": data['secret']
        }
        users.append(new_user)
        user_counter += 1
        return jsonify({"message": "User created successfully", "user": new_user})

    def get(self):
        result = [{"id": user['id'], "login": user['login']} for user in users]
        return jsonify(result)


# Ресурс для просмотра методов шифрования
class MethodResource(Resource):
    def get(self):
        return jsonify(methods)


# Ресурс для управления сеансами шифрования
class SessionResource(Resource):
    def post(self):
        global session_counter
        data = request.get_json()
        user_id = data['user_id']
        method_id = data['method_id']

        # Проверка наличия пользователя и метода
        user = next((u for u in users if u['id'] == user_id), None)
        method = next((m for m in methods if m['id'] == method_id), None)
        if not user:
            return jsonify({"message": "User not found"}), 404
        if not method:
            return jsonify({"message": "Method not found"}), 404

        # Подготовка данных для шифрования
        data_in = data['data_in'].upper()
        data_in = ''.join(filter(lambda x: x in ALPHABET, data_in))
        params = data.get('params', {})
        start_time = datetime.now()

        # Выполнение шифрования
        if method['caption'] == "CAESAR":
            shift = int(params.get('shift', 0))
            data_out = caesar_cipher(data_in, shift)
        elif method['caption'] == "VIGENERE":
            key = params.get('key', '')
            data_out = vigenere_cipher(data_in, key)

        end_time = datetime.now()
        time_op = (end_time - start_time).total_seconds()

        # Создание нового сеанса шифрования
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
        return jsonify({"message": "Encryption session created successfully", "session": new_session})

    def get(self, session_id):
        session = next((s for s in sessions if s['id'] == session_id), None)
        if not session:
            return jsonify({"message": "Session not found"}), 404
        return jsonify(session)

    def delete(self, session_id):
        data = request.get_json()
        session = next((s for s in sessions if s['id'] == session_id), None)
        if not session:
            return jsonify({"message": "Session not found"}), 404
        user = next((u for u in users if u['id'] == session['user_id']), None)
        if user['secret'] != data['secret']:
            return jsonify({"message": "Unauthorized"}), 401
        sessions.remove(session)
        return jsonify({"message": "Session deleted successfully"})


# Добавление ресурсов в API
api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(MethodResource, '/methods')
api.add_resource(SessionResource, '/sessions', '/sessions/<int:session_id>')

if __name__ == '__main__':
    app.run(debug=True)
