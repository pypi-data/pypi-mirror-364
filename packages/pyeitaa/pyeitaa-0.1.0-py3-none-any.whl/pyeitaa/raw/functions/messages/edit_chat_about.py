from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditChatAbout(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2109f869``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        about: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "about"]

    ID = -0x2109f869
    QUALNAME = "functions.messages.EditChatAbout"

    def __init__(self, *, peer: "raw.base.InputPeer", about: str) -> None:
        self.peer = peer  # InputPeer
        self.about = about  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        about = String.read(data)
        
        return EditChatAbout(peer=peer, about=about)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(String(self.about))
        
        return data.getvalue()
