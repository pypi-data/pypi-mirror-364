from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class RecentMeUrlChatInvite(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RecentMeUrl`.

    Details:
        - Layer: ``135``
        - ID: ``-0x14b6f7e3``

    Parameters:
        url: ``str``
        chat_invite: :obj:`ChatInvite <pyeitaa.raw.base.ChatInvite>`
    """

    __slots__: List[str] = ["url", "chat_invite"]

    ID = -0x14b6f7e3
    QUALNAME = "types.RecentMeUrlChatInvite"

    def __init__(self, *, url: str, chat_invite: "raw.base.ChatInvite") -> None:
        self.url = url  # string
        self.chat_invite = chat_invite  # ChatInvite

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        chat_invite = TLObject.read(data)
        
        return RecentMeUrlChatInvite(url=url, chat_invite=chat_invite)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        data.write(self.chat_invite.write())
        
        return data.getvalue()
