from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PhoneCallDiscarded(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhoneCall`.

    Details:
        - Layer: ``135``
        - ID: ``0x50ca4de1``

    Parameters:
        id: ``int`` ``64-bit``
        need_rating (optional): ``bool``
        need_debug (optional): ``bool``
        video (optional): ``bool``
        reason (optional): :obj:`PhoneCallDiscardReason <pyeitaa.raw.base.PhoneCallDiscardReason>`
        duration (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "need_rating", "need_debug", "video", "reason", "duration"]

    ID = 0x50ca4de1
    QUALNAME = "types.PhoneCallDiscarded"

    def __init__(self, *, id: int, need_rating: Optional[bool] = None, need_debug: Optional[bool] = None, video: Optional[bool] = None, reason: "raw.base.PhoneCallDiscardReason" = None, duration: Optional[int] = None) -> None:
        self.id = id  # long
        self.need_rating = need_rating  # flags.2?true
        self.need_debug = need_debug  # flags.3?true
        self.video = video  # flags.6?true
        self.reason = reason  # flags.0?PhoneCallDiscardReason
        self.duration = duration  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        need_rating = True if flags & (1 << 2) else False
        need_debug = True if flags & (1 << 3) else False
        video = True if flags & (1 << 6) else False
        id = Long.read(data)
        
        reason = TLObject.read(data) if flags & (1 << 0) else None
        
        duration = Int.read(data) if flags & (1 << 1) else None
        return PhoneCallDiscarded(id=id, need_rating=need_rating, need_debug=need_debug, video=video, reason=reason, duration=duration)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.need_rating else 0
        flags |= (1 << 3) if self.need_debug else 0
        flags |= (1 << 6) if self.video else 0
        flags |= (1 << 0) if self.reason is not None else 0
        flags |= (1 << 1) if self.duration is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        if self.reason is not None:
            data.write(self.reason.write())
        
        if self.duration is not None:
            data.write(Int(self.duration))
        
        return data.getvalue()
