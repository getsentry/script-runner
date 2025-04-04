from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any

import requests
from flask import Request
from google.auth import default, jwt
from google.auth.exceptions import GoogleAuthError
from googleapiclient.discovery import Resource, build


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
        user_header = request.headers[self.USER_HEADER_KEY]
        prefix = "accounts.google.com:"
        if user_header.startswith(prefix):
            prefix_len = len(prefix)
            return user_header[prefix_len:]
        else:
            raise UnauthorizedUser(f"Invalid user header format: {user_header}")

    @cached_property
    def __google_certs(self) -> Any:
        """
        Returns a dictionary of Google's public certificates.
        """
        return requests.get("https://www.gstatic.com/iap/verify/public_key").json()

    @cached_property
    def __service(self) -> Resource:
        credentials, _proj = default()  # type: ignore
        return build("cloudidentity", "v1", credentials=credentials)

    def __is_user_in_google_group(self, user_email: str, group_email: str) -> bool:
        group = self.__service.groups().lookup(groupKey_id=group_email).execute()
        member = (
            self.__service.groups()
            .memberships()
            .lookup(parent=group["name"], memberKey_id=user_email)
            .execute()
        )

        if member["email"] == user_email:
            return True
        return False

    def authenticate_request(self, request: Request) -> None:
        user_email = self.get_user_email(request)
        jwt_assertion = request.headers[self.JWT_HEADER_KEY]

        data = request.get_json()
        # Authentication applies on the /run and /run_region endpoints where there is always a group
        group = data["group"]

        try:
            decoded_token = jwt.decode(
                jwt_assertion,
                certs=self.__google_certs,
                audience=self.audience,
                clock_skew_in_seconds=30,
            )  # type: ignore

            assert user_email == decoded_token["email"]

        except (GoogleAuthError, KeyError, AssertionError) as e:
            raise UnauthorizedUser from e

        for principal in self.iap_principals[group]:
            if self.__is_user_in_google_group(user_email, principal):
                return None

        raise UnauthorizedUser("User is not in group")

    def has_group_access(self, request: Request, group: str) -> bool:
        try:
            user_email = self.get_user_email(request)
        except UnauthorizedUser:
            return False

        for i in self.iap_principals[group]:
            if self.__is_user_in_google_group(user_email, i):
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
