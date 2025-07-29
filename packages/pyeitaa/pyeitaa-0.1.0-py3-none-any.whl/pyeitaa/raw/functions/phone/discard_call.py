from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class DiscardCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4d343e40``

    Parameters:
        peer: :obj:`InputPhoneCall <pyeitaa.raw.base.InputPhoneCall>`
        duration: ``int`` ``32-bit``
        reason: :obj:`PhoneCallDiscardReason <pyeitaa.raw.base.PhoneCallDiscardReason>`
        connection_id: ``int`` ``64-bit``
        video (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "duration", "reason", "connection_id", "video"]

    ID = -0x4d343e40
    QUALNAME = "functions.phone.DiscardCall"

    def __init__(self, *, peer: "raw.base.InputPhoneCall", duration: int, reason: "raw.base.PhoneCallDiscardReason", connection_id: int, video: Optional[bool] = None) -> None:
        self.peer = peer  # InputPhoneCall
        self.duration = duration  # int
        self.reason = reason  # PhoneCallDiscardReason
        self.connection_id = connection_id  # long
        self.video = video  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        video = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        duration = Int.read(data)
        
        reason = TLObject.read(data)
        
        connection_id = Long.read(data)
        
        return DiscardCall(peer=peer, duration=duration, reason=reason, connection_id=connection_id, video=video)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.video else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Int(self.duration))
        
        data.write(self.reason.write())
        
        data.write(Long(self.connection_id))
        
        return data.getvalue()
