from .travelers import travelers_bp
from .countries import countries_bp
from .trips import trips_bp
from .home import home_bp
from .employees import employees_bp
from .login import auth_bp
from .app import app_bp
from .notifications import notifications_bp
from .stages import stages_bp
from .companions import companions_bp

# lista wszystkich blueprintów w jednym miejscu
all_blueprints = [
    travelers_bp,
    countries_bp,
    trips_bp,
    home_bp,
    employees_bp,
    auth_bp,
    app_bp,
    notifications_bp,
    stages_bp,
    companions_bp
]