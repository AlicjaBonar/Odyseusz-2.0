from .travelers import travelers_bp
from .countries import countries_bp
from .trips import trips_bp

# lista wszystkich blueprintów w jednym miejscu
all_blueprints = [
    travelers_bp,
    countries_bp,
    trips_bp
]