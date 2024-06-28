from flask import Blueprint

def register_routes(app):
    from .users import user_bp
    from .methods import method_bp
    from .sessions import session_bp
    from .break_cipher import break_cipher_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(method_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(break_cipher_bp)
