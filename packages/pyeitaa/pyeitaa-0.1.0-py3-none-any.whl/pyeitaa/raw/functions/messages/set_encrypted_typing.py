from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetEncryptedTyping(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x791451ed``

    Parameters:
        peer: :obj:`InputEncryptedChat <pyeitaa.raw.base.InputEncryptedChat>`
        typing: ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "typing"]

    ID = 0x791451ed
    QUALNAME = "functions.messages.SetEncryptedTyping"

    def __init__(self, *, peer: "raw.base.InputEncryptedChat", typing: bool) -> None:
        self.peer = peer  # InputEncryptedChat
        self.typing = typing  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        typing = Bool.read(data)
        
        return SetEncryptedTyping(peer=peer, typing=typing)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Bool(self.typing))
        
        return data.getvalue()
