from models import db, User, Session


class UserService:

    @staticmethod
    def add_user(data):
        if not UserService.is_unique_login(data['login']) or not UserService.is_unique_secret(data['secret']):
            return {"error": "Login or Secret must be unique", "status": 400}
        user = User(username=data["login"], secret_key=data["secret"])
        db.session.add(user)
        db.session.commit()
        return {"id": user.id, "login": user.username, "status": 201}

    @staticmethod
    def list_users():
        users = User.query.all()
        return [{"login": user.username, "id": user.id} for user in users]

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if user:
            # Удаляем все связанные сессии перед удалением пользователя
            Session.query.filter_by(user_id=user_id).delete()
            db.session.delete(user)
            db.session.commit()
            return {"status": "deleted", "status_code": 200}
        else:
            return {"error": "User not found", "status_code": 404}

    @staticmethod
    def is_unique_login(login):
        return User.query.filter_by(username=login).first() is None

    @staticmethod
    def is_unique_secret(secret):
        return User.query.filter_by(secret_key=secret).first() is None
