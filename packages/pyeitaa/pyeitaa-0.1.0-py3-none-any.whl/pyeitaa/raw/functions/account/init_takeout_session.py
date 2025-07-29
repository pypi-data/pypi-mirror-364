from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class InitTakeoutSession(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xfa4b7fc``

    Parameters:
        contacts (optional): ``bool``
        message_users (optional): ``bool``
        message_chats (optional): ``bool``
        message_megagroups (optional): ``bool``
        message_channels (optional): ``bool``
        files (optional): ``bool``
        file_max_size (optional): ``int`` ``32-bit``

    Returns:
        :obj:`account.Takeout <pyeitaa.raw.base.account.Takeout>`
    """

    __slots__: List[str] = ["contacts", "message_users", "message_chats", "message_megagroups", "message_channels", "files", "file_max_size"]

    ID = -0xfa4b7fc
    QUALNAME = "functions.account.InitTakeoutSession"

    def __init__(self, *, contacts: Optional[bool] = None, message_users: Optional[bool] = None, message_chats: Optional[bool] = None, message_megagroups: Optional[bool] = None, message_channels: Optional[bool] = None, files: Optional[bool] = None, file_max_size: Optional[int] = None) -> None:
        self.contacts = contacts  # flags.0?true
        self.message_users = message_users  # flags.1?true
        self.message_chats = message_chats  # flags.2?true
        self.message_megagroups = message_megagroups  # flags.3?true
        self.message_channels = message_channels  # flags.4?true
        self.files = files  # flags.5?true
        self.file_max_size = file_max_size  # flags.5?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        contacts = True if flags & (1 << 0) else False
        message_users = True if flags & (1 << 1) else False
        message_chats = True if flags & (1 << 2) else False
        message_megagroups = True if flags & (1 << 3) else False
        message_channels = True if flags & (1 << 4) else False
        files = True if flags & (1 << 5) else False
        file_max_size = Int.read(data) if flags & (1 << 5) else None
        return InitTakeoutSession(contacts=contacts, message_users=message_users, message_chats=message_chats, message_megagroups=message_megagroups, message_channels=message_channels, files=files, file_max_size=file_max_size)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.contacts else 0
        flags |= (1 << 1) if self.message_users else 0
        flags |= (1 << 2) if self.message_chats else 0
        flags |= (1 << 3) if self.message_megagroups else 0
        flags |= (1 << 4) if self.message_channels else 0
        flags |= (1 << 5) if self.files else 0
        flags |= (1 << 5) if self.file_max_size is not None else 0
        data.write(Int(flags))
        
        if self.file_max_size is not None:
            data.write(Int(self.file_max_size))
        
        return data.getvalue()
