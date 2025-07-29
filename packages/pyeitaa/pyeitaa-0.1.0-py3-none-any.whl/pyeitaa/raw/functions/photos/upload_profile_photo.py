from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Double
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UploadProfilePhoto(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x760cf097``

    Parameters:
        file (optional): :obj:`InputFile <pyeitaa.raw.base.InputFile>`
        video (optional): :obj:`InputFile <pyeitaa.raw.base.InputFile>`
        video_start_ts (optional): ``float`` ``64-bit``

    Returns:
        :obj:`photos.Photo <pyeitaa.raw.base.photos.Photo>`
    """

    __slots__: List[str] = ["file", "video", "video_start_ts"]

    ID = -0x760cf097
    QUALNAME = "functions.photos.UploadProfilePhoto"

    def __init__(self, *, file: "raw.base.InputFile" = None, video: "raw.base.InputFile" = None, video_start_ts: Optional[float] = None) -> None:
        self.file = file  # flags.0?InputFile
        self.video = video  # flags.1?InputFile
        self.video_start_ts = video_start_ts  # flags.2?double

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        file = TLObject.read(data) if flags & (1 << 0) else None
        
        video = TLObject.read(data) if flags & (1 << 1) else None
        
        video_start_ts = Double.read(data) if flags & (1 << 2) else None
        return UploadProfilePhoto(file=file, video=video, video_start_ts=video_start_ts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.file is not None else 0
        flags |= (1 << 1) if self.video is not None else 0
        flags |= (1 << 2) if self.video_start_ts is not None else 0
        data.write(Int(flags))
        
        if self.file is not None:
            data.write(self.file.write())
        
        if self.video is not None:
            data.write(self.video.write())
        
        if self.video_start_ts is not None:
            data.write(Double(self.video_start_ts))
        
        return data.getvalue()
