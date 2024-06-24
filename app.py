from flask import Flask, request, jsonify
from utils.encryption import vigenere_encrypt, vigenere_decrypt, shift_encrypt, shift_decrypt, get_alphabet
import datetime

app = Flask(__name__)

users = []
methods = [
    {"id": 1, "name": "vigenere", "caption": "Vigenere Cipher", "params": {"key": "str"},
     "description": "Шифрование методом Виженера"},
    {"id": 2, "name": "shift", "caption": "Shift Cipher", "params": {"shift": "int"},
     "description": "Шифрование методом сдвига"}
]
sessions = []


def is_unique_login(login):
    return all(user['login'] != login for user in users)


def is_unique_secret(secret):
    return all(user['secret'] != secret for user in users)


@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    if not is_unique_login(data['login']) or not is_unique_secret(data['secret']):
        return jsonify({"error": "Login or Secret must be unique"}), 400
    user = {
        "id": len(users) + 1,
        "login": data["login"],
        "secret": data["secret"]
    }
    users.append(user)
    return jsonify(user), 201


@app.route('/users', methods=['GET'])
def list_users():
    return jsonify([{"login": user["login"], "id": user["id"]} for user in users]), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        users.remove(user)
        # Удалить все сессии, связанные с этим пользователем
        global sessions
        sessions = [session for session in sessions if session["user_id"] != user_id]
        return jsonify({"status": "deleted"}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/methods', methods=['GET'])
def list_methods():
    return jsonify(methods), 200


@app.route('/sessions', methods=['POST'])
def create_session():
    data = request.json
    user_id = data.get("user_id")
    method_id = data.get("method_id")
    text = data.get("text")
    params = data.get("params")
    operation = data.get("operation", "encrypt")
    language = data.get("language", "en")

    method = next((m for m in methods if m["id"] == method_id), None)
    if not method:
        return jsonify({"error": "Unknown method"}), 400

    try:
        alphabet = get_alphabet(language)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    start_time = datetime.datetime.now()

    if method["name"] == "vigenere":
        key = params.get("key")
        if operation == "encrypt":
            result_text = vigenere_encrypt(text, key, alphabet)
        else:
            result_text = vigenere_decrypt(text, key, alphabet)
    elif method["name"] == "shift":
        shift = params.get("shift")
        if operation == "encrypt":
            result_text = shift_encrypt(text, shift, alphabet)
        else:
            result_text = shift_decrypt(text, shift, alphabet)
    else:
        return jsonify({"error": "Unknown method"}), 400

    end_time = datetime.datetime.now()
    elapsed_time = (end_time - start_time).total_seconds()

    session = {
        "id": len(sessions) + 1,
        "user_id": user_id,
        "method_id": method_id,
        "data_in": text,
        "params": params,
        "data_out": result_text,
        "status": "completed",
        "created_at": start_time.isoformat(),
        "time_out": elapsed_time
    }
    sessions.append(session)
    return jsonify(session), 201


@app.route('/sessions', methods=['GET'])
def list_sessions():
    return jsonify(sessions), 200


@app.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    data = request.json
    secret = data.get("secret")

    session = next((s for s in sessions if s["id"] == session_id), None)
    if session:
        user = next((u for u in users if u["id"] == session["user_id"]), None)
        if user and user["secret"] == secret:
            sessions.remove(session)
            return jsonify({"status": "deleted"}), 200
        else:
            return jsonify({"error": "Invalid secret"}), 403
    else:
        return jsonify({"error": "Session not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
