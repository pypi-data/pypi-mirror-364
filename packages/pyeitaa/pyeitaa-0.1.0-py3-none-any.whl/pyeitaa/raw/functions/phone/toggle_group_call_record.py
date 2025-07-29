from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ToggleGroupCallRecord(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xed738f8``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        start (optional): ``bool``
        video (optional): ``bool``
        title (optional): ``str``
        video_portrait (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "start", "video", "title", "video_portrait"]

    ID = -0xed738f8
    QUALNAME = "functions.phone.ToggleGroupCallRecord"

    def __init__(self, *, call: "raw.base.InputGroupCall", start: Optional[bool] = None, video: Optional[bool] = None, title: Optional[str] = None, video_portrait: Optional[bool] = None) -> None:
        self.call = call  # InputGroupCall
        self.start = start  # flags.0?true
        self.video = video  # flags.2?true
        self.title = title  # flags.1?string
        self.video_portrait = video_portrait  # flags.2?Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        start = True if flags & (1 << 0) else False
        video = True if flags & (1 << 2) else False
        call = TLObject.read(data)
        
        title = String.read(data) if flags & (1 << 1) else None
        video_portrait = Bool.read(data) if flags & (1 << 2) else None
        return ToggleGroupCallRecord(call=call, start=start, video=video, title=title, video_portrait=video_portrait)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.start else 0
        flags |= (1 << 2) if self.video else 0
        flags |= (1 << 1) if self.title is not None else 0
        flags |= (1 << 2) if self.video_portrait is not None else 0
        data.write(Int(flags))
        
        data.write(self.call.write())
        
        if self.title is not None:
            data.write(String(self.title))
        
        if self.video_portrait is not None:
            data.write(Bool(self.video_portrait))
        
        return data.getvalue()
