import sentry_sdk
from flask import Flask

from script_runner.approval_policy import ApprovalPolicy
from script_runner.approval_store import ApprovalStore
from script_runner.blueprints.base_app_bp import base_app_bp
from script_runner.blueprints.main_config_bp import main_config_bp
from script_runner.blueprints.region_config_bp import region_config_bp
from script_runner.blueprints.static_routes_bp import static_files_bp
from script_runner.config import config, configure_approvals
from script_runner.utils import CombinedConfig, MainConfig, RegionConfig


def create_flask_app(
    approval_policy: ApprovalPolicy, approval_store: ApprovalStore | None
) -> Flask:
    """
    Create a Flask app instance.
    """
    if config.sentry_dsn:
        sentry_sdk.init(
            dsn=config.sentry_dsn,
        )

    configure_approvals(approval_policy, approval_store)

    app = Flask(__name__)
    app.register_blueprint(base_app_bp)

    if isinstance(config, (MainConfig, CombinedConfig)):
        app.register_blueprint(static_files_bp)

    if isinstance(config, (MainConfig, CombinedConfig)):
        app.register_blueprint(main_config_bp)

    if isinstance(config, (RegionConfig, CombinedConfig)):
        app.register_blueprint(region_config_bp)

    return app
