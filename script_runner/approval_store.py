from abc import ABC, abstractmethod
from enum import StrEnum
from typing import TypedDict


class ApprovalRequestStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    EXECUTED = "executed"


class ApprovalRequest(TypedDict):
    id: str
    function: str
    args: list[str]
    regions: list[str]
    requested_by: str
    deadline: float
    status: ApprovalRequestStatus


class ApprovalException(Exception):
    pass


class ApprovalStore(ABC):
    @abstractmethod
    def list_approval_requests(self, group: str) -> list[ApprovalRequest]:
        """
        Lists all requests for a group.
        """
        raise NotImplementedError

    @abstractmethod
    def create_approval_request(
        self,
        group: str,
        function: str,
        args: list[str],
        regions: list[str],
        requested_by: str,
    ) -> ApprovalRequest:
        """
        Create the approval request.
        """
        raise NotImplementedError

    @abstractmethod
    def approve_request(
        self,
        request_id: str,
        group: str,
        approved_by: str,
    ) -> ApprovalRequest:
        """
        Marks the function `approved`. `approved_by` is the email of the approving user.
        """
        raise NotImplementedError

    @abstractmethod
    def execute_request(
        self,
        request_id: str,
        group: str,
        executed_by: str,
    ) -> None:
        """
        Marks the request as executed. Must be executed by the user who created the request.
        """
        raise NotImplementedError

    @abstractmethod
    def cancel_request(
        self,
        request_id: str,
        group: str,
        cancelled_by: str,
    ) -> None:
        """
        Cancels a request. Can be cancelled by any user in the group.
        """
        raise NotImplementedError
