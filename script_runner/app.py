from flask import Flask

from script_runner.app_blueprint import app_blueprint

app = Flask(__name__)
app.register_blueprint(app_blueprint)
