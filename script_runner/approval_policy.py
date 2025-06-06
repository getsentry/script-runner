from abc import ABC, abstractmethod
from script_runner.utils import Function
from enum import Enum


class ApprovalStatus(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class ApprovalPolicy(ABC):
    @abstractmethod
    def requires_approval(
        self, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        """
        Either allow, deny, or enable user to request approval.
        """
        raise NotImplementedError


class AllowAll(ApprovalPolicy):
    def requires_approval(
        self, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        return ApprovalStatus.ALLOW


class Readonly(ApprovalPolicy):
    def requires_approval(
        self, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        if function.is_readonly:
            return ApprovalStatus.ALLOW

        return ApprovalStatus.DENY


class RequireWriteApproval(ApprovalPolicy):
    def requires_approval(
        self, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        if function.is_readonly:
            return ApprovalStatus.ALLOW

        return ApprovalStatus.REQUIRE_APPROVAL
