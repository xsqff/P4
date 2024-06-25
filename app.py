from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///encryption.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

ALPHABET = " ,.:(_)-0123456789AБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), unique=True, nullable=False)
    secret = db.Column(db.String(30), nullable=False)

class Method(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(30), nullable=False)
    json_params = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    method_id = db.Column(db.Integer, db.ForeignKey('method.id'), nullable=False)
    data_in = db.Column(db.String(10000), nullable=False)
    params = db.Column(db.String(1000), nullable=True)
    data_out = db.Column(db.String(10000), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_op = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

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
    key = [ALPHABET.index(k) for k in key]
    key_length = len(key)
    for i, char in enumerate(text):
        if char in ALPHABET:
            key_idx = key[i % key_length]
            idx = (ALPHABET.index(char) + (-key_idx if decrypt else key_idx)) % len(ALPHABET)
            result.append(ALPHABET[idx])
        else:
            result.append(char)
    return ''.join(result)

class UserResource(Resource):
    def post(self):
        data = request.get_json()
        new_user = User(login=data['login'], secret=data['secret'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully", "user": {"id": new_user.id, "login": new_user.login}})

    def get(self):
        users = User.query.all()
        result = [{"id": user.id, "login": user.login} for user in users]
        return jsonify(result)

class MethodResource(Resource):
    def get(self):
        methods = Method.query.all()
        result = [{"id": method.id, "caption": method.caption, "json_params": method.json_params, "description": method.description} for method in methods]
        return jsonify(result)

class SessionResource(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        method_id = data['method_id']
        user = User.query.get(user_id)
        method = Method.query.get(method_id)

        if not user:
            return jsonify({"message": "User not found"}), 404
        if not method:
            return jsonify({"message": "Method not found"}), 404

        data_in = data['data_in'].upper()
        data_in = ''.join(filter(lambda x: x in ALPHABET, data_in))
        params = data.get('params', {})
        start_time = datetime.now()

        if method.caption == "CAESAR":
            shift = int(params.get('shift', 0))
            data_out = caesar_cipher(data_in, shift)
        elif method.caption == "VIGENERE":
            key = params.get('key', '')
            data_out = vigenere_cipher(data_in, key)

        end_time = datetime.now()
        time_op = (end_time - start_time).total_seconds()

        new_session = Session(
            user_id=user_id,
            method_id=method_id,data_in=data_in,
            params=str(params),
            data_out=data_out,
            status="completed",
            time_op=time_op
        )
        db.session.add(new_session)
        db.session.commit()
        return jsonify({"message": "Encryption session created successfully", "session": {"id": new_session.id, "data_out": new_session.data_out}})

    def get(self, session_id):
        session = Session.query.get(session_id)
        if not session:
            return jsonify({"message": "Session not found"}), 404
        return jsonify({
            "id": session.id,
            "user_id": session.user_id,
            "method_id": session.method_id,
            "data_in": session.data_in,
            "params": session.params,
            "data_out": session.data_out,
            "status": session.status,
            "created_at": session.created_at,
            "time_op": session.time_op
        })

    def delete(self, session_id):
        data = request.get_json()
        session = Session.query.get(session_id)
        if not session:
            return jsonify({"message": "Session not found"}), 404
        user = User.query.get(session.user_id)
        if user.secret != data['secret']:
            return jsonify({"message": "Unauthorized"}), 401
        db.session.delete(session)
        db.session.commit()
        return jsonify({"message": "Session deleted successfully"})

class AllSessionsResource(Resource):
    def get(self):
        sessions = Session.query.all()
        result = [{
            "id": session.id,
            "user_id": session.user_id,
            "method_id": session.method_id,
            "data_in": session.data_in,
            "params": session.params,
            "data_out": session.data_out,
            "status": session.status,
            "created_at": session.created_at,
            "time_op": session.time_op
        } for session in sessions]
        return jsonify(result)

api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(MethodResource, '/methods')
api.add_resource(SessionResource, '/sessions', '/sessions/<int:session_id>')
api.add_resource(AllSessionsResource, '/sessions')

if name == '__main__':
    with app.app_context():
        # Create initial methods if they don't exist
        if not Method.query.filter_by(caption="CAESAR").first():
            caesar_method = Method(caption="CAESAR", json_params='{"shift": "int"}', description="Caesar cipher")
            db.session.add(caesar_method)
        if not Method.query.filter_by(caption="VIGENERE").first():
            vigenere_method = Method(caption="VIGENERE", json_params='{"key": "string"}', description="Vigenere cipher")
            db.session.add(vigenere_method)
        db.session.commit()
    app.run(debug=True)