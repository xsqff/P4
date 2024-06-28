from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    secret_key = db.Column(db.String(120), unique=True, nullable=False)

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    method_id = db.Column(db.Integer, nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    parameters = db.Column(db.JSON, nullable=False)
    output_data = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    processing_time = db.Column(db.Float, nullable=False)
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
