import os

from script_runner.app import create_flask_app
from script_runner.approval_policy import AllowAll

config_file_path = os.getenv("CONFIG_FILE_PATH")
policy = AllowAll()
store = None

app = create_flask_app(config_file_path, policy, store)
