from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetChatInviteImporters(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x26fb7289``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        link: ``str``
        offset_date: ``int`` ``32-bit``
        offset_user: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`messages.ChatInviteImporters <pyeitaa.raw.base.messages.ChatInviteImporters>`
    """

    __slots__: List[str] = ["peer", "link", "offset_date", "offset_user", "limit"]

    ID = 0x26fb7289
    QUALNAME = "functions.messages.GetChatInviteImporters"

    def __init__(self, *, peer: "raw.base.InputPeer", link: str, offset_date: int, offset_user: "raw.base.InputUser", limit: int) -> None:
        self.peer = peer  # InputPeer
        self.link = link  # string
        self.offset_date = offset_date  # int
        self.offset_user = offset_user  # InputUser
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        link = String.read(data)
        
        offset_date = Int.read(data)
        
        offset_user = TLObject.read(data)
        
        limit = Int.read(data)
        
        return GetChatInviteImporters(peer=peer, link=link, offset_date=offset_date, offset_user=offset_user, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(String(self.link))
        
        data.write(Int(self.offset_date))
        
        data.write(self.offset_user.write())
        
        data.write(Int(self.limit))
        
        return data.getvalue()
