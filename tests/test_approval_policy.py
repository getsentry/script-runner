from script_runner.approval_policy import ReadonlyUnlessSuperuser, ApprovalStatus
from script_runner.auth import GoogleAuth, UnauthorizedUser
from flask import Request
from unittest.mock import Mock


ALLOWED_USER_EMAIL = "allowed_user@test.com"

class FakeGoogleAuth(GoogleAuth):
    """
    Fake google auth. allowed_user@test.com is allowed,
    and "allowed_group" is allowed. Everything else is unauthorized.
    """


    def authenticate_request(self, request: Request) -> None:
        user_email = self.get_user_email(request)
        if user_email != ALLOWED_USER_EMAIL:
            raise UnauthorizedUser("invalid user email")

    def has_group_access(self, request: Request, group: str) -> bool:
        try:
            user_email = self.get_user_email(request)
        except UnauthorizedUser:
            return False

        if user_email == ALLOWED_USER_EMAIL:
            return True
        return False


def test_readonly_unless_superuser() -> None:
    superusers = {"region_one": [ALLOWED_USER_EMAIL], "region_two": []}
    policy = ReadonlyUnlessSuperuser(superusers)
    policy.set_auth_method(FakeGoogleAuth("foo", {}))
    mock_request = Mock(headers={"X-Goog-Authenticated-User-Email": f"accounts.google.com:{ALLOWED_USER_EMAIL}"})
    mock_request_no_access = Mock(headers={"X-Goog-Authenticated-User-Email": f"accounts.google.com:other@test.com"})

    # read is always allowed
    assert policy.requires_approval(mock_request, "group", Mock(is_readonly=True), ["region_one"]) == ApprovalStatus.ALLOW

    # write is allowed for superuser
    assert policy.requires_approval(mock_request, "group", Mock(is_readonly=False), ["region_one"]) == ApprovalStatus.ALLOW

    # write is not allowed for non-superuser
    assert policy.requires_approval(mock_request_no_access, "group", Mock(is_readonly=False), ["region_one"]) == ApprovalStatus.DENY
