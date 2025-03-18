from datetime import datetime, timedelta, UTC
from typing import Literal, Optional


class Cookie:
    VALID_SAME_SITE = ("Strict", "Lax", "None")

    def __init__(
        self,
        name: str,
        value: str,
        *,
        domain: Optional[str] = None,
        expires: Optional[datetime] = None,
        http_only: bool = False,
        max_age: Optional[int] = None,
        partitioned: bool = False,
        path: Optional[str] = None,
        secure: bool = False,
        same_site: Optional[Literal["Lax", "None", "Strict"]] = None,
    ) -> None:
        self.name = name
        self.value = value
        self.domain = domain
        self.expires = expires
        self.http_only = http_only
        self.max_age = max_age
        self.partitioned = partitioned
        self.path = path
        self.secure = secure
        if same_site and same_site not in self.VALID_SAME_SITE:
            raise ValueError(f"Invalid samesite value: {same_site}, should be one of {self.VALID_SAME_SITE}")
        if same_site == "None" and secure is False:
            raise ValueError("If SameSite=None, Secure must be True")
        self.same_site = same_site

    def __str__(self) -> str:
        cookie = f"{self.name}={self.value}"
        if self.domain:
            cookie += f"; Domain={self.domain}"
        if self.expires:
            cookie += f"; Expires={self.expires.strftime('%a, %d %b %Y %H:%M:%S GMT')}"
        if self.http_only:
            cookie += "; HttpOnly"
        if self.max_age:
            cookie += f"; Max-Age={self.max_age}"
        if self.partitioned:
            cookie += "; Partitioned"
        if self.path:
            cookie += f"; Path={self.path}"
        if self.secure:
            cookie += "; Secure"
        if self.same_site:
            cookie += f"; SameSite={self.same_site}"
        return cookie


def expiration_time(seconds: int) -> datetime:
    return datetime.now(UTC) + timedelta(seconds=seconds)


def expiration_as_ttl(dt: datetime) -> int:
    return int(dt.timestamp())
