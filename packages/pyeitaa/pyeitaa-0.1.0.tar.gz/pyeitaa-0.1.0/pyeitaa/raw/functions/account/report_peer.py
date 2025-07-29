from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReportPeer(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3a45c27a``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        reason: :obj:`ReportReason <pyeitaa.raw.base.ReportReason>`
        message: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "reason", "message"]

    ID = -0x3a45c27a
    QUALNAME = "functions.account.ReportPeer"

    def __init__(self, *, peer: "raw.base.InputPeer", reason: "raw.base.ReportReason", message: str) -> None:
        self.peer = peer  # InputPeer
        self.reason = reason  # ReportReason
        self.message = message  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        reason = TLObject.read(data)
        
        message = String.read(data)
        
        return ReportPeer(peer=peer, reason=reason, message=message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.reason.write())
        
        data.write(String(self.message))
        
        return data.getvalue()
