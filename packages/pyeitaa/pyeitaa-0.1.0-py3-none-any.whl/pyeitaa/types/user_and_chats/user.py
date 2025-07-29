import html
import logging
from datetime import datetime
from typing import Optional, Self

import pyeitaa

from ...utils import timestamp_to_datetime
from ...enums import ParseMode, UserStatus
from ...raw.base import UserStatus as BaseUserStatus
from ...raw.types import (
    UserEmpty,
    User as User_,
    UserProfilePhoto,
    UserStatusLastMonth,
    UserStatusLastWeek,
    UserStatusRecently,
    UserStatusOffline,
    UserStatusOnline,
    UpdateUserStatus
)

from ..object import Object
from ..update import Update

log = logging.getLogger(__name__)


class Link(str):
    HTML = "<a href={url}>{text}</a>"
    MARKDOWN = "[{text}]({url})"

    def __init__(self, url: str, text: str, style: ParseMode):
        super().__init__()

        self.url = url
        self.text = text
        self.style = style

    @staticmethod
    def format(url: str, text: str, style: ParseMode):
        fmt = Link.MARKDOWN if style == ParseMode.MARKDOWN else Link.HTML

        return fmt.format(url=url, text=html.escape(text))

    # noinspection PyArgumentList
    def __new__(cls, url, text, style):
        return str.__new__(cls, Link.format(url, text, style))

    def __call__(self, other: str = None, *, style: str = None):
        return Link.format(self.url, other or self.text, style or self.style)

    def __str__(self):
        return Link.format(self.url, self.text, self.style)


class User(Object, Update):
    def __init__(
        self,
        *,
        client: "pyeitaa.Client" = None,
        id: int,
        is_self: Optional[bool] = None,
        is_contact: Optional[bool] = None,
        is_mutual_contact: Optional[bool] = None,
        is_deleted: Optional[bool] = None,
        is_bot: Optional[bool] = None,
        is_scam: Optional[bool] = None,
        is_support: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        is_restricted: Optional[bool] = None,
        is_min: Optional[bool] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        status: Optional[UserStatus] = None,
        last_online_date: Optional[datetime] = None,
        next_offline_date: Optional[datetime] = None,
        username: Optional[str] = None,
        language_code: Optional[str] = None,
        phone_number: Optional[str] = None,
        photo: Optional[UserProfilePhoto] = None,
        raw: Optional[User_] = None
    ):
        super().__init__(client)

        self.id = id
        self.is_self = is_self
        self.is_contact = is_contact
        self.is_mutual_contact = is_mutual_contact
        self.is_deleted = is_deleted
        self.is_bot = is_bot
        self.is_restricted = is_restricted
        self.is_scam = is_scam
        self.is_support = is_support
        self.is_verified = is_verified
        self.is_min = is_min
        self.first_name = first_name
        self.last_name = last_name
        self.status = status
        self.last_online_date = last_online_date
        self.next_offline_date = next_offline_date
        self.username = username
        self.language_code = language_code
        self.phone_number = phone_number
        self.photo = photo
        self.raw = raw

    @property
    def full_name(self) -> str:
        return " ".join(filter(None, [self.first_name, self.last_name])) or None

    @property
    def mention(self):
        return Link(
            f"et://user?id={self.id}",
            self.first_name or "Deleted Account",
            self._client.parse_mode
        )

    @staticmethod
    def _parse(client, user: User_) -> Optional[Self]:
        if user is None or isinstance(user, UserEmpty):
            return None

        return User(
            id=user.id,
            is_self=user.is_self,
            is_contact=user.contact,
            is_mutual_contact=user.mutual_contact,
            is_deleted=user.deleted,
            is_bot=user.bot,
            is_restricted=user.restricted,
            is_support=user.support,
            is_min=user.min,
            first_name=user.first_name,
            last_name=user.last_name,
            **User._parse_status(user.status, user.bot),
            username=user.username,
            language_code=user.lang_code,
            phone_number=user.phone,
            photo=user.photo,
            raw=user,
            client=client
        )

    @staticmethod
    def _parse_status(user_status: BaseUserStatus, is_bot: bool = False) -> dict[str, Optional[datetime]]:
        if is_bot:
            return dict.fromkeys(("status", "last_online_date", "next_offline_date"), None)

        last_online_date = None
        next_offline_date = None

        match user_status:
            case UserStatusOnline():
                status, date = UserStatus.ONLINE, user_status.expires
                next_offline_date = timestamp_to_datetime(date)

            case UserStatusOffline():
                status, date = UserStatus.OFFLINE, user_status.was_online
                last_online_date = timestamp_to_datetime(date)

            case UserStatusRecently():
                status, date = UserStatus.RECENTLY, None

            case UserStatusLastWeek():
                status, date = UserStatus.LAST_WEEK, None
            
            case UserStatusLastMonth():
                status, date = UserStatus.LAST_MONTH, None

            case _:
                status, date = UserStatus.LONG_AGO, None

        return {
            "status": status,
            "last_online_date": last_online_date,
            "next_offline_date": next_offline_date
        }

    @staticmethod
    def _parse_user_status(client, user_status: UpdateUserStatus):
        return User(
            id=user_status.user_id,
            **User._parse_status(user_status.status),
            raw=user_status,
            client=client
        )
