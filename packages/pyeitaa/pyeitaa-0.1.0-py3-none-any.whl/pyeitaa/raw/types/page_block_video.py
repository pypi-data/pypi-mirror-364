from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PageBlockVideo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``0x7c8fe7b6``

    Parameters:
        video_id: ``int`` ``64-bit``
        caption: :obj:`PageCaption <pyeitaa.raw.base.PageCaption>`
        autoplay (optional): ``bool``
        loop (optional): ``bool``
    """

    __slots__: List[str] = ["video_id", "caption", "autoplay", "loop"]

    ID = 0x7c8fe7b6
    QUALNAME = "types.PageBlockVideo"

    def __init__(self, *, video_id: int, caption: "raw.base.PageCaption", autoplay: Optional[bool] = None, loop: Optional[bool] = None) -> None:
        self.video_id = video_id  # long
        self.caption = caption  # PageCaption
        self.autoplay = autoplay  # flags.0?true
        self.loop = loop  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        autoplay = True if flags & (1 << 0) else False
        loop = True if flags & (1 << 1) else False
        video_id = Long.read(data)
        
        caption = TLObject.read(data)
        
        return PageBlockVideo(video_id=video_id, caption=caption, autoplay=autoplay, loop=loop)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.autoplay else 0
        flags |= (1 << 1) if self.loop else 0
        data.write(Int(flags))
        
        data.write(Long(self.video_id))
        
        data.write(self.caption.write())
        
        return data.getvalue()
