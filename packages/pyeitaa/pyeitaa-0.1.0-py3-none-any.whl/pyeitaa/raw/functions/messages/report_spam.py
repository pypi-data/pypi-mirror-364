from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReportSpam(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x30ea6d25``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer"]

    ID = -0x30ea6d25
    QUALNAME = "functions.messages.ReportSpam"

    def __init__(self, *, peer: "raw.base.InputPeer") -> None:
        self.peer = peer  # InputPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        return ReportSpam(peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        return data.getvalue()
