from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetChatTheme(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x19c41ec1``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        emoticon: ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "emoticon"]

    ID = -0x19c41ec1
    QUALNAME = "functions.messages.SetChatTheme"

    def __init__(self, *, peer: "raw.base.InputPeer", emoticon: str) -> None:
        self.peer = peer  # InputPeer
        self.emoticon = emoticon  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        emoticon = String.read(data)
        
        return SetChatTheme(peer=peer, emoticon=emoticon)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(String(self.emoticon))
        
        return data.getvalue()
