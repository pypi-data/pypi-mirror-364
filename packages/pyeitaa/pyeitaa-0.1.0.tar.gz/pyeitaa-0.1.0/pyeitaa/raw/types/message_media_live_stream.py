from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageMediaLiveStream(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x340bc6da``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        state: :obj:`LiveStreamState <pyeitaa.raw.base.LiveStreamState>`
        from_self (optional): ``bool``
        total_viewers (optional): ``int`` ``32-bit``
        thumbs (optional): List of :obj:`PhotoSize <pyeitaa.raw.base.PhotoSize>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["id", "access_hash", "state", "from_self", "total_viewers", "thumbs"]

    ID = -0x340bc6da
    QUALNAME = "types.MessageMediaLiveStream"

    def __init__(self, *, id: int, access_hash: int, state: "raw.base.LiveStreamState", from_self: Optional[bool] = None, total_viewers: Optional[int] = None, thumbs: Optional[List["raw.base.PhotoSize"]] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.state = state  # LiveStreamState
        self.from_self = from_self  # flags.1?true
        self.total_viewers = total_viewers  # flags.0?int
        self.thumbs = thumbs  # flags.2?Vector<PhotoSize>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        from_self = True if flags & (1 << 1) else False
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        total_viewers = Int.read(data) if flags & (1 << 0) else None
        state = TLObject.read(data)
        
        thumbs = TLObject.read(data) if flags & (1 << 2) else []
        
        return MessageMediaLiveStream(id=id, access_hash=access_hash, state=state, from_self=from_self, total_viewers=total_viewers, thumbs=thumbs)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.from_self else 0
        flags |= (1 << 0) if self.total_viewers is not None else 0
        flags |= (1 << 2) if self.thumbs is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        if self.total_viewers is not None:
            data.write(Int(self.total_viewers))
        
        data.write(self.state.write())
        
        if self.thumbs is not None:
            data.write(Vector(self.thumbs))
        
        return data.getvalue()
