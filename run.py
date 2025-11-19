from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app)
app.config['WTF_CSRF_ENABLED'] = False

if __name__ == "__main__":
    app.run(debug=True)
