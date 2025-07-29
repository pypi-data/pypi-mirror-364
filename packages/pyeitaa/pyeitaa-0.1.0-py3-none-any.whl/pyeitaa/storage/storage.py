from abc import ABC, abstractmethod
from typing import Optional, Any


class Storage(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def create(self) -> None:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def update_peers(self, peers: list[tuple[int, Optional[int], str, Optional[str], Optional[str]]]) -> None:
        pass

    @abstractmethod
    def get_peer(self, attribute: Any, query: str):
        pass

    @abstractmethod
    def get_session_attribute(self, attribute: str) -> str | int:
        pass

    @abstractmethod
    def set_session_attribute(self, attribute: str, value: str | int) -> None:
        pass

    @abstractmethod
    def get_full_session(self) -> tuple[str, str, int]:
        pass

    @abstractmethod
    def get_peer_by_id(self, peer_id: int):
        pass

    @abstractmethod
    def get_peer_by_username(self, username: str):
        pass

    @abstractmethod
    def get_peer_by_phone_number(self, phone_number: str):
        pass

    @property
    @abstractmethod
    def token(self) -> str:
        pass

    @token.setter
    @abstractmethod
    def token(self, token: str) -> None:
        pass

    @property
    @abstractmethod
    def imei(self) -> str:
        pass

    @imei.setter
    @abstractmethod
    def imei(self, imei: str) -> None:
        pass

    @property
    @abstractmethod
    def date(self) -> int:
        pass

    @date.setter
    @abstractmethod
    def date(self, date: str) -> None:
        pass

    @property
    @abstractmethod
    def user_id(self) -> int:
        pass

    @user_id.setter
    @abstractmethod
    def user_id(self, user_id: str) -> None:
        pass
