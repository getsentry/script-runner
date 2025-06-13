import sentry_sdk
from flask import Flask

from script_runner.approval_policy import ApprovalPolicy
from script_runner.approval_store import ApprovalStore
from script_runner.blueprints.base_app_bp import base_app_bp
from script_runner.blueprints.main_bp import create_main_bp
from script_runner.blueprints.region_bp import create_region_bp
from script_runner.blueprints.static_routes_bp import static_files_bp
from script_runner.config import configure
from script_runner.utils import CombinedConfig, MainConfig, RegionConfig


def create_flask_app(
    config_file_path: str,
    approval_policy: ApprovalPolicy,
    approval_store: ApprovalStore | None,
) -> Flask:
    """
    Create a Flask app instance.
    """

    app_config = configure(config_file_path, approval_policy, approval_store)
    config = app_config.config

    if config.sentry_dsn:
        sentry_sdk.init(
            dsn=config.sentry_dsn,
        )

    app = Flask(__name__)
    app.register_blueprint(base_app_bp)

    if isinstance(config, (MainConfig, CombinedConfig)):
        app.register_blueprint(static_files_bp)

    if isinstance(config, (MainConfig, CombinedConfig)):
        main_bp = create_main_bp(app_config)
        app.register_blueprint(main_bp)

    if isinstance(config, (RegionConfig, CombinedConfig)):
        region_bp = create_region_bp(app_config)
        app.register_blueprint(region_bp)

    return app
