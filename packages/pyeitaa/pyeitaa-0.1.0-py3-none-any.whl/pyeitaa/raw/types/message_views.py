from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageViews(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageViews`.

    Details:
        - Layer: ``135``
        - ID: ``0x455b853d``

    Parameters:
        views (optional): ``int`` ``32-bit``
        forwards (optional): ``int`` ``32-bit``
        replies (optional): :obj:`MessageReplies <pyeitaa.raw.base.MessageReplies>`
    """

    __slots__: List[str] = ["views", "forwards", "replies"]

    ID = 0x455b853d
    QUALNAME = "types.MessageViews"

    def __init__(self, *, views: Optional[int] = None, forwards: Optional[int] = None, replies: "raw.base.MessageReplies" = None) -> None:
        self.views = views  # flags.0?int
        self.forwards = forwards  # flags.1?int
        self.replies = replies  # flags.2?MessageReplies

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        views = Int.read(data) if flags & (1 << 0) else None
        forwards = Int.read(data) if flags & (1 << 1) else None
        replies = TLObject.read(data) if flags & (1 << 2) else None
        
        return MessageViews(views=views, forwards=forwards, replies=replies)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.views is not None else 0
        flags |= (1 << 1) if self.forwards is not None else 0
        flags |= (1 << 2) if self.replies is not None else 0
        data.write(Int(flags))
        
        if self.views is not None:
            data.write(Int(self.views))
        
        if self.forwards is not None:
            data.write(Int(self.forwards))
        
        if self.replies is not None:
            data.write(self.replies.write())
        
        return data.getvalue()
