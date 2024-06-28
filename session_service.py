from datetime import datetime
from models import db, Session, User
from services.encryption_service import encrypt_text
from methods import get_method_name


class SessionService:

    @staticmethod
    def create_session(data):
        user_id = data.get("user_id")
        method_id = data.get("method_id")
        text = data.get("text")
        params = data.get("params")
        operation = data.get("operation", "encrypt")
        language = data.get("language", "en")

        method_name = get_method_name(method_id)
        if not method_name:
            return {"error": "Unknown method", "status": 400}

        start_time = datetime.now()
        result_text = encrypt_text(text, method_name, params, operation, language)
        end_time = datetime.now()

        session = Session(
            user_id=user_id,
            method_id=method_id,
            input_data=text,
            parameters=params,
            output_data=result_text,
            status="completed",
            created_at=start_time,
            processing_time=(end_time - start_time).total_seconds()
        )
        db.session.add(session)
        db.session.commit()

        return {
            "id": session.id,
            "user_id": session.user_id,
            "method_id": session.method_id,
            "data_in": session.input_data,
            "params": session.parameters,
            "data_out": session.output_data,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "time_out": session.processing_time,
            "status": 201
        }

    @staticmethod
    def list_sessions():
        sessions = Session.query.all()
        return [{
            "id": session.id,
            "user_id": session.user_id,
            "method_id": session.method_id,
            "data_in": session.input_data,
            "params": session.parameters,
            "data_out": session.output_data,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "time_out": session.processing_time
        } for session in sessions]

    @staticmethod
    def delete_session(session_id, data):
        secret = data.get("secret")
        session = Session.query.get(session_id)
        if session:
            user = User.query.get(session.user_id)
            if user and user.secret_key == secret:
                db.session.delete(session)
                db.session.commit()
                return {"status": "deleted", "status_code": 200}
            else:
                return {"error": "Invalid secret", "status_code": 403}
        else:
            return {"error": "Session not found", "status_code": 404}
