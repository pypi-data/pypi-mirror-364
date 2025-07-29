from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReadEncryptedHistory(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7f4b690a``

    Parameters:
        peer: :obj:`InputEncryptedChat <pyeitaa.raw.base.InputEncryptedChat>`
        max_date: ``int`` ``32-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "max_date"]

    ID = 0x7f4b690a
    QUALNAME = "functions.messages.ReadEncryptedHistory"

    def __init__(self, *, peer: "raw.base.InputEncryptedChat", max_date: int) -> None:
        self.peer = peer  # InputEncryptedChat
        self.max_date = max_date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        max_date = Int.read(data)
        
        return ReadEncryptedHistory(peer=peer, max_date=max_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.max_date))
        
        return data.getvalue()
