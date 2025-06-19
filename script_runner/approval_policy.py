from abc import ABC, abstractmethod
from enum import Enum

from flask import Request

from script_runner.auth import AuthMethod, GoogleAuth
from script_runner.utils import Function


class ApprovalStatus(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class ApprovalPolicy(ABC):
    def set_auth_method(self, auth_method: AuthMethod) -> None:
        """
        Called after initialization so that the approval policies can
        access the configured method and check group membership.
        """
        self.auth_method = auth_method

    @abstractmethod
    def requires_approval_one_region(
        self, request: Request, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        """
        Either allow, deny, or enable user to request approval.
        """
        raise NotImplementedError

    def requires_approval(
        self, request: Request, group_name: str, func: Function, regions: list[str]
    ) -> ApprovalStatus:
        """
        Check if a function requires approval for a list of regions.
        Returns the strictest approval requirement if they vary by region.
        """
        statuses = set()

        for region in regions:
            statuses.add(
                self.requires_approval_one_region(request, group_name, func, region)
            )

        if ApprovalStatus.DENY in statuses:
            return ApprovalStatus.DENY

        if ApprovalStatus.REQUIRE_APPROVAL in statuses:
            return ApprovalStatus.REQUIRE_APPROVAL

        return ApprovalStatus.ALLOW


class AllowAll(ApprovalPolicy):
    def requires_approval_one_region(
        self, request: Request, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        return ApprovalStatus.ALLOW


class Readonly(ApprovalPolicy):
    def requires_approval_one_region(
        self, request: Request, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        if function.is_readonly:
            return ApprovalStatus.ALLOW

        return ApprovalStatus.DENY


class RequireWriteApproval(ApprovalPolicy):
    def requires_approval_one_region(
        self, request: Request, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        if function.is_readonly:
            return ApprovalStatus.ALLOW

        return ApprovalStatus.REQUIRE_APPROVAL


class ReadonlyUnlessSuperuser(ApprovalPolicy):
    """
    Allows only users in specific superuser groups access to write functions.
    Can only be used with Google as auth method.
    """

    def __init__(self, superuser_groups_by_region: dict[str, list[str]]):
        # map of region name to list of superuser google groups for that region
        self.superuser_groups_by_region = superuser_groups_by_region

    def set_auth_method(self, auth_method: AuthMethod) -> None:
        """
        Called after initialization so that the approval policies can
        access the configured method and check group membership.
        """
        super().set_auth_method(auth_method)
        assert isinstance(self.auth_method, GoogleAuth)

        cls = type(self.auth_method)
        self.auth_method = cls(
            audience=self.auth_method.audience,
            iap_principals=self.superuser_groups_by_region,
        )

    def requires_approval_one_region(
        self, request: Request, group: str, function: Function, region: str
    ) -> ApprovalStatus:
        # read is always allowed
        if function.is_readonly:
            return ApprovalStatus.ALLOW

        # write is only allowed if the user is in one of the superuser groups
        if self.auth_method.has_group_access(request, group):
            return ApprovalStatus.ALLOW

        return ApprovalStatus.DENY
