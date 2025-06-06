from __future__ import annotations

from dataclasses import dataclass

from script_runner.utils import load_config, Function
from script_runner.approval_store import ApprovalStore
from script_runner.approval_policy import ApprovalPolicy, ApprovalStatus

config = load_config()


"""
Global variable to store the approval state
"""
_APPROVALS: Approvals | None = None


@dataclass(frozen=True)
class Approvals:
    policy: ApprovalPolicy
    store: ApprovalStore | None

    def requires_approval(
        self, group_name: str, func: Function, regions: list[str]
    ) -> ApprovalStatus:
        """
        Check if a function requires approval for a list of regions.
        Returns the strictest approval requirement if they vary by region.
        """
        statuses = set()

        for region in regions:
            statuses.add(self.policy.requires_approval(group_name, func, region))

        if ApprovalStatus.DENY in statuses:
            return ApprovalStatus.DENY

        if ApprovalStatus.REQUIRE_APPROVAL in statuses:
            return ApprovalStatus.REQUIRE_APPROVAL

        return ApprovalStatus.ALLOW


def configure_approvals(policy: ApprovalPolicy, store: ApprovalStore | None) -> None:
    """
    This gets run before the app is created.
    """
    global _APPROVALS

    if _APPROVALS is not None:
        raise RuntimeError("Approvals has already been configured.")

    _APPROVALS = Approvals(policy, store)


def get_approvals() -> Approvals:
    """
    Can only be called after `configure_approvals` has been called once.
    """
    if _APPROVALS is None:
        raise RuntimeError("Approvals has not been set.")

    return _APPROVALS
