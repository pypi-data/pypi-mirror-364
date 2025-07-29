from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetExportedChatInvite(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x73746f5c``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        link: ``str``

    Returns:
        :obj:`messages.ExportedChatInvite <pyeitaa.raw.base.messages.ExportedChatInvite>`
    """

    __slots__: List[str] = ["peer", "link"]

    ID = 0x73746f5c
    QUALNAME = "functions.messages.GetExportedChatInvite"

    def __init__(self, *, peer: "raw.base.InputPeer", link: str) -> None:
        self.peer = peer  # InputPeer
        self.link = link  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        link = String.read(data)
        
        return GetExportedChatInvite(peer=peer, link=link)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(String(self.link))
        
        return data.getvalue()
