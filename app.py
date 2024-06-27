
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from datetime import datetime
import sqlite3

app = Flask(__name__)
api = Api(app)

ALPHABET = " ,.:(_)-0123456789AБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

# Database initialization
def init_db():
    conn = sqlite3.connect('encryption.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            login TEXT UNIQUE NOT NULL,
            secret TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS methods (
            id INTEGER PRIMARY KEY,
            caption TEXT NOT NULL,
            json_params TEXT NOT NULL,
            description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            method_id INTEGER,
            data_in TEXT,
            params TEXT,
            data_out TEXT,
            status TEXT,
            created_at TEXT,
            time_op TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(method_id) REFERENCES methods(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

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
        data = request.get_json()
        login = data['login']
        secret = data['secret']
        conn = sqlite3.connect('encryption.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (login, secret) VALUES (?, ?)", (login, secret))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return jsonify({"message": "User created successfully", "user": {"id": user_id, "login": login}})

    def get(self):
        conn = sqlite3.connect('encryption.db')
        c = conn.cursor()
        c.execute("SELECT id, login FROM users")
        users = c.fetchall()
        conn.close()
        result = [{"id": user[0], "login": user[1]} for user in users]
        return jsonify(result)

class MethodResource(Resource):
    def get(self):
        conn = sqlite3.connect('encryption.db')
        c = conn.cursor()
        c.execute("SELECT * FROM methods")
        methods = c.fetchall()
        conn.close()
        result = [{"id": method[0], "caption": method[1], "json_params": method[2], "description": method[3]} for method in methods]
        return jsonify(result)

class SessionResource(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        method_id = data['method_id']
        data_in = data['data_in'].upper()
        data_in = ''.join(filter(lambda x: x in ALPHABET, data_in))
        params = data.get('params', {})
        decrypt = data.get('decrypt', False)
        start_time = datetime.now()

        conn = sqlite3.connect('encryption.db')
        c = conn.cursor()
        c.execute("SELECT caption FROM methods WHERE id = ?", (method_id,))
        method = c.fetchone()
        if not method:
            return jsonify({"message": "Method not found"}), 404
        method_caption = method[0]

        if method_caption == "CAESAR":
            shift = int(params.get('shift', 0))
            data_out = caesar_cipher(data_in, shift, decrypt=decrypt)
        elif method_caption == "VIGENERE":
            key = params.get('key', '')
            data_out = vigenere_cipher(data_in, key, decrypt=decrypt)

        end_time = datetime.now()
        time_op = (end_time - start_time).total_seconds()

        c.execute('''
            INSERT INTO sessions (user_id, method_id, data_in, params, data_out, status, created_at, time_op)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, method_id, data_in, str(params), data_out, "completed", datetime.now().isoformat(), str(time_op)))
        conn.commit()
        session_id = c.lastrowid
        conn.close()
        return jsonify({"message": "Encryption session created successfully", "session": {"id": session_id, "data_out": data_out, "time_op": time_op}})

    def get(self, session_id):
        conn = sqlite3.connect('encryption.db')
        c = conn.cursor()
        c.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        session = c.fetchone()
        conn.close()
        if not session:
            return jsonify({"message": "Session not found"}), 404
        result = {
            "id": session[0],
            "user_id": session[1],
            "method_id": session[2],
            "data_in": session[3],
            "params": session[4],
            "data_out": session[5],
            "status": session[6],
            "created_at": session[7],
            "time_op": session[8]
        }
        return jsonify(result)

    def delete(self, session_id):
        data = request.get_json()
        secret = data['secret']
        conn = sqlite3.connect('encryption.db')
        c = conn.cursor()
        c.execute("SELECT user_id FROM sessions WHERE id = ?", (session_id,))
        session = c.fetchone()
        if not session:
            return jsonify({"message": "Session not found"}), 404
        user_id = session[0]
        c.execute("SELECT secret FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if not user or user[0] != secret:
            return jsonify({"message": "Unauthorized"}), 401
        c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Session deleted successfully"})

class HackSessionResource(Resource):
    def post(self):
        data = request.get_json()
        session_id = data['session_id']
        conn = sqlite3.connect('encryption.db')
        c = conn.cursor()
        c.execute("SELECT data_in, method_id FROM sessions WHERE id = ?", (session_id,))
        session = c.fetchone()
        if not session:
            return jsonify({"message": "Session not found"}), 404
        data_in, method_id = session
        c.execute("SELECT caption FROM methods WHERE id = ?", (method_id,))
        method = c.fetchone()
        if not method:
            return jsonify({"message": "Method not found"}), 404
        method_caption = method[0]

        if method_caption == "CAESAR":
            for shift in range(len(ALPHABET)):
                data_out = caesar_cipher(data_in, shift, decrypt=True)
                if 'СЕКРЕТ' in data_out or 'ПРИМЕР' in data_out:
                    conn.close()
                    return jsonify({"message": "Caesar cipher hacked successfully", "data_out": data_out, "shift": shift})
        elif method_caption == "VIGENERE":
            # Simple example for Vigenere cipher hack, assuming key length of 3
            for k1 in ALPHABET:
                for k2 in ALPHABET:
                    for k3 in ALPHABET:
                        data_out = vigenere_cipher(data_in, key, decrypt=True)
                        if 'СЕКРЕТ' in data_out or 'ПРИМЕР' in data_out:
                            conn.close()
                            return jsonify(
                                {"message": "Vigenere cipher hacked successfully", "data_out": data_out, "key": key})
        conn.close()
        return jsonify({"message": "Failed to hack the cipher"})

# Initial methods
def add_initial_methods():
    conn = sqlite3.connect('encryption.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM methods")
    count = c.fetchone()[0]
    if count == 0:
        c.execute("INSERT INTO methods (caption, json_params, description) VALUES (?, ?, ?)",
                  ("CAESAR", '{"shift": "int"}', "Caesar cipher"))
        c.execute("INSERT INTO methods (caption, json_params, description) VALUES (?, ?, ?)",
                  ("VIGENERE", '{"key": "string"}', "Vigenere cipher"))
    conn.commit()
    conn.close()

add_initial_methods()

api.add_resource(UserResource, '/users')
api.add_resource(MethodResource, '/methods')
api.add_resource(SessionResource, '/sessions', '/sessions/<int:session_id>')
api.add_resource(HackSessionResource, '/hack_session')

if __name__ == '__main__':
    app.run(debug=True)