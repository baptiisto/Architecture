from flask import Flask
from dotenv import load_dotenv
import os
def create_app():
    load_dotenv(os.getenv("PDM_SCRIPT_ENV_FILE"))
    from toudou.todo_blueprint import todo_blueprint
    app = Flask(__name__)
    app.config.from_prefixed_env(prefix="TOUDOU_FLASK")
    # Register the blueprint
    app.register_blueprint(todo_blueprint)

    return app
