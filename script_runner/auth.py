import functools
from abc import ABC, abstractmethod
from typing import Any

import requests
from flask import Request
from google.auth import jwt
from google.auth.exceptions import GoogleAuthError


class UnauthorizedUser(Exception):
    pass


class AuthMethod(ABC):
    @abstractmethod
    def authenticate_request(self, request: Request) -> None:
        """
        Raise UnauthorizedUser exception if the request cannot be authenticated.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_email(self, request: Request) -> str | None:
        """
        Returns the email of the authenticated user.
        """
        raise NotImplementedError

    def has_group_access(self, request: Request, group: str) -> bool:
        """
        Returns True if the user has access to the specified group.
        """
        raise NotImplementedError


class GoogleAuth(AuthMethod):
    def __init__(self, audience: str, iap_principals: dict[str, list[str]]):
        self.audience = audience
        self.iap_principals: dict[str, list[str]] = iap_principals
        self.USER_HEADER_KEY = "X-Goog-Authenticated-User-Email"
        self.JWT_HEADER_KEY = "X-Goog-Iap-Jwt-Assertion"

    def get_user_email(self, request: Request) -> str:
        return request.headers[self.USER_HEADER_KEY]

    @functools.lru_cache(maxsize=1)
    def __get_google_certs(self) -> Any:
        """
        Returns a dictionary of Google's public certificates.
        """
        return requests.get("https://www.gstatic.com/iap/verify/public_key").json()

    def __is_user_in_google_group(self, user_email: str, group_email: str) -> bool:
        # TODO: Implement this function
        return True

    def authenticate_request(self, request: Request) -> None:
        user_email = request.headers[self.USER_HEADER_KEY]
        jwt_assertion = request.headers[self.JWT_HEADER_KEY]

        data = request.get_json()
        # Authentication applies on the /run and /run_region endpoints where there is always a group
        group = data["group"]
        principals = self.iap_principals[group]

        try:
            decoded_token = jwt.decode(
                jwt_assertion, certs=self.__get_google_certs(), audience=self.audience
            )  # type: ignore

            print("decoded token", decoded_token)

            assert user_email == decoded_token["email"]

        except (GoogleAuthError, KeyError) as e:
            raise UnauthorizedUser from e

        for principal in principals:
            if self.__is_user_in_google_group(user_email, principal):
                return None

        raise UnauthorizedUser("User is not in group")

    def has_group_access(self, request: Request, group: str) -> bool:
        for i in self.iap_principals[group]:
            if self.__is_user_in_google_group(self.get_user_email(request), i):
                return True
        return False


class NoAuth(AuthMethod):
    def authenticate_request(self, request: Request) -> None:
        # No authentication required
        pass

    def get_user_email(self, request: Request) -> None:
        return None

    def has_group_access(self, request: Request, group: str) -> bool:
        return True
