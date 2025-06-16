from abc import ABC, abstractmethod
from enum import Enum

from script_runner.utils import Function


class ApprovalStatus(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class ApprovalPolicy(ABC):
    @abstractmethod
    def requires_approval_one_region(
        self, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        """
        Either allow, deny, or enable user to request approval.
        """
        raise NotImplementedError

    def requires_approval(
        self, group_name: str, func: Function, regions: list[str]
    ) -> ApprovalStatus:
        """
        Check if a function requires approval for a list of regions.
        Returns the strictest approval requirement if they vary by region.
        """
        statuses = set()

        for region in regions:
            statuses.add(self.requires_approval_one_region(group_name, func, region))

        if ApprovalStatus.DENY in statuses:
            return ApprovalStatus.DENY

        if ApprovalStatus.REQUIRE_APPROVAL in statuses:
            return ApprovalStatus.REQUIRE_APPROVAL

        return ApprovalStatus.ALLOW


class AllowAll(ApprovalPolicy):
    def requires_approval_one_region(
        self, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        return ApprovalStatus.ALLOW


class Readonly(ApprovalPolicy):
    def requires_approval_one_region(
        self, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        if function.is_readonly:
            return ApprovalStatus.ALLOW

        return ApprovalStatus.DENY


class RequireWriteApproval(ApprovalPolicy):
    def requires_approval_one_region(
        self, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        if function.is_readonly:
            return ApprovalStatus.ALLOW

        return ApprovalStatus.REQUIRE_APPROVAL
