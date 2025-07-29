from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReportProfilePhoto(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x573390b``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        photo_id: :obj:`InputPhoto <pyeitaa.raw.base.InputPhoto>`
        reason: :obj:`ReportReason <pyeitaa.raw.base.ReportReason>`
        message: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "photo_id", "reason", "message"]

    ID = -0x573390b
    QUALNAME = "functions.account.ReportProfilePhoto"

    def __init__(self, *, peer: "raw.base.InputPeer", photo_id: "raw.base.InputPhoto", reason: "raw.base.ReportReason", message: str) -> None:
        self.peer = peer  # InputPeer
        self.photo_id = photo_id  # InputPhoto
        self.reason = reason  # ReportReason
        self.message = message  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        photo_id = TLObject.read(data)
        
        reason = TLObject.read(data)
        
        message = String.read(data)
        
        return ReportProfilePhoto(peer=peer, photo_id=photo_id, reason=reason, message=message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.photo_id.write())
        
        data.write(self.reason.write())
        
        data.write(String(self.message))
        
        return data.getvalue()
