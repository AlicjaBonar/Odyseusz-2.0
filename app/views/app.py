from flask import Blueprint, render_template

app_bp = Blueprint("app_bp", __name__)

@app_bp.route("/")
def index_page():
    return render_template("index.html")

@app_bp.route("/login_page")
def login_page():
    return render_template("login.html")

@app_bp.route("/register_traveler_page")
def register_traveler_page():
    return render_template("register_traveler.html")

@app_bp.route("/register_employee_page")
def register_employee_page():
    return render_template("register_employee.html")
