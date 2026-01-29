from flask import Flask, g
from app.database.database import SessionLocal, engine, Base
from sqlalchemy.exc import SQLAlchemyError
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from app.repositories import EmployeeRepository, TravelerRepository
from app.database.database import SessionLocal

csrf = CSRFProtect()
login_manager = LoginManager()

def create_app():
    print("Initializing Flask application...")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersekretnyklucz123'

    csrf.init_app(app)
    login_manager.login_view = "auth.login_page"

    @login_manager.user_loader
    def load_user(user_id):
        db = SessionLocal()
        try:
        # Flask-Login przechowuje ID jako string, rzutujemy na int
            u_id = int(user_id)

            user = EmployeeRepository(db).find_by_id(u_id)
            if user:
                return user
            
            return TravelerRepository(db).find_by_id(u_id)
        finally:
            db.close()
    
    login_manager.init_app(app)
    
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
