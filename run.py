from app import create_app
from flask_cors import CORS
from flask import Flask
from flask_login import LoginManager
from app.models import Traveler, Employee

app = create_app()
CORS(app)
app.config['WTF_CSRF_ENABLED'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login_page"

if __name__ == "__main__":
    app.run(debug=True)
