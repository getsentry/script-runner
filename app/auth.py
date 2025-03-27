from abc import abstractmethod

from flask import Request


class UnauthorizedUser(Exception):
    pass


class AuthMethod:
    @abstractmethod
    def authenticate_request(self, request: Request) -> None:
        """
        Raise UnauthorizedUser exception if the request cannot be authenticated.
        """
        raise NotImplementedError


class GoogleAuth(AuthMethod):
    def __init__(self, audience: str, iap_principals: dict[str, list[str]]):
        self.audience = audience
        self.iap_principals: dict[str, list[str]] = iap_principals

    def authenticate_request(self, request: Request) -> None:
        # TODO: Implement the authentication logic
        pass


class NoAuth(AuthMethod):
    def authenticate_request(self, request: Request) -> None:
        # No authentication required
        pass
