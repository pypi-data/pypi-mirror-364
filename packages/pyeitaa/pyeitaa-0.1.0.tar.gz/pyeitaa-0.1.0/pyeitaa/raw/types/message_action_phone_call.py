from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageActionPhoneCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7f1ee581``

    Parameters:
        call_id: ``int`` ``64-bit``
        video (optional): ``bool``
        reason (optional): :obj:`PhoneCallDiscardReason <pyeitaa.raw.base.PhoneCallDiscardReason>`
        duration (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["call_id", "video", "reason", "duration"]

    ID = -0x7f1ee581
    QUALNAME = "types.MessageActionPhoneCall"

    def __init__(self, *, call_id: int, video: Optional[bool] = None, reason: "raw.base.PhoneCallDiscardReason" = None, duration: Optional[int] = None) -> None:
        self.call_id = call_id  # long
        self.video = video  # flags.2?true
        self.reason = reason  # flags.0?PhoneCallDiscardReason
        self.duration = duration  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        video = True if flags & (1 << 2) else False
        call_id = Long.read(data)
        
        reason = TLObject.read(data) if flags & (1 << 0) else None
        
        duration = Int.read(data) if flags & (1 << 1) else None
        return MessageActionPhoneCall(call_id=call_id, video=video, reason=reason, duration=duration)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.video else 0
        flags |= (1 << 0) if self.reason is not None else 0
        flags |= (1 << 1) if self.duration is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.call_id))
        
        if self.reason is not None:
            data.write(self.reason.write())
        
        if self.duration is not None:
            data.write(Int(self.duration))
        
        return data.getvalue()
