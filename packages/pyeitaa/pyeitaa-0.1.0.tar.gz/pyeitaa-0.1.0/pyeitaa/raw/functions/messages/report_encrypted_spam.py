from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReportEncryptedSpam(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x4b0c8c0f``

    Parameters:
        peer: :obj:`InputEncryptedChat <pyeitaa.raw.base.InputEncryptedChat>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer"]

    ID = 0x4b0c8c0f
    QUALNAME = "functions.messages.ReportEncryptedSpam"

    def __init__(self, *, peer: "raw.base.InputEncryptedChat") -> None:
        self.peer = peer  # InputEncryptedChat

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        return ReportEncryptedSpam(peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        return data.getvalue()
