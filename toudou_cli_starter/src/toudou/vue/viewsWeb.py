from flask import Flask
from dotenv import load_dotenv
import os
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash ,check_password_hash


def create_app():
    load_dotenv(os.getenv("PDM_SCRIPT_ENV_FILE"))
    from toudou.vue.todo_blueprint import todo_blueprint
    app = Flask(__name__)
    app.config.from_prefixed_env(prefix="TOUDOU_FLASK")

    app.register_blueprint(todo_blueprint)

    return app

auth = HTTPBasicAuth()

users = {
    "user": {
        "password": generate_password_hash("user"),
        "role": "user"
    },
    "admin": {
        "password": generate_password_hash("admin"),
        "role": "admin"
    }
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users[username]["password"], password):
        return username

@auth.get_user_roles
def get_user_roles(username):
    if username in users:
        return [users[username]["role"]]
    else:
        return []
