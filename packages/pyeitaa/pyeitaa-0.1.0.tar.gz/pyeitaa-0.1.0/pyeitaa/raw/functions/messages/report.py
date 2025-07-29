from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Report(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x76ac54b2``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        id: List of ``int`` ``32-bit``
        reason: :obj:`ReportReason <pyeitaa.raw.base.ReportReason>`
        message: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "id", "reason", "message"]

    ID = -0x76ac54b2
    QUALNAME = "functions.messages.Report"

    def __init__(self, *, peer: "raw.base.InputPeer", id: List[int], reason: "raw.base.ReportReason", message: str) -> None:
        self.peer = peer  # InputPeer
        self.id = id  # Vector<int>
        self.reason = reason  # ReportReason
        self.message = message  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        id = TLObject.read(data, Int)
        
        reason = TLObject.read(data)
        
        message = String.read(data)
        
        return Report(peer=peer, id=id, reason=reason, message=message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Vector(self.id, Int))
        
        data.write(self.reason.write())
        
        data.write(String(self.message))
        
        return data.getvalue()
