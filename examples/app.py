from script_runner.app import create_flask_app
from script_runner.approval_policy import AllowAll

policy = AllowAll()

store = None

app = create_flask_app(policy, store)
