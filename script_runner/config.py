from dataclasses import dataclass

from script_runner.approval_policy import ApprovalPolicy
from script_runner.approval_store import ApprovalStore
from script_runner.utils import CombinedConfig, MainConfig, RegionConfig, load_config


@dataclass(frozen=True)
class Config:
    config: CombinedConfig | MainConfig | RegionConfig
    approval_policy: ApprovalPolicy
    approval_store: ApprovalStore | None


def configure(
    config_file_path: str, policy: ApprovalPolicy, store: ApprovalStore | None
) -> Config:
    """
    This gets run once before the app is created.
    """
    config = load_config(config_file_path)
    policy.set_auth_method(config.auth)

    return Config(config, policy, store)
