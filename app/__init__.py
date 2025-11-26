from flask import Flask, g
from app.database.database import SessionLocal, engine, Base
from sqlalchemy.exc import SQLAlchemyError
from flask_wtf import CSRFProtect

csrf = CSRFProtect()

def create_app():
    print("Initializing Flask application...")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersekretnyklucz123'

    csrf.init_app(app)

    # Tworzenie tabel (jeśli nie istnieją)
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")

    # Rejestracja blueprintów
    from app.views import all_blueprints

    for bp in all_blueprints:
        app.register_blueprint(bp)



    # Tworzenie i zamykanie sesji bazy
    @app.before_request
    def create_session():
        g.db = SessionLocal()

    @app.teardown_request
    def shutdown_session(exception=None):
        SessionLocal.remove()

    return app
