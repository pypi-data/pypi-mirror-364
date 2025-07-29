from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class AutoDownloadSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.AutoDownloadSettings`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1fbdcd0d``

    Parameters:
        photo_size_max: ``int`` ``32-bit``
        video_size_max: ``int`` ``32-bit``
        file_size_max: ``int`` ``32-bit``
        video_upload_maxbitrate: ``int`` ``32-bit``
        disabled (optional): ``bool``
        video_preload_large (optional): ``bool``
        audio_preload_next (optional): ``bool``
        phonecalls_less_data (optional): ``bool``
    """

    __slots__: List[str] = ["photo_size_max", "video_size_max", "file_size_max", "video_upload_maxbitrate", "disabled", "video_preload_large", "audio_preload_next", "phonecalls_less_data"]

    ID = -0x1fbdcd0d
    QUALNAME = "types.AutoDownloadSettings"

    def __init__(self, *, photo_size_max: int, video_size_max: int, file_size_max: int, video_upload_maxbitrate: int, disabled: Optional[bool] = None, video_preload_large: Optional[bool] = None, audio_preload_next: Optional[bool] = None, phonecalls_less_data: Optional[bool] = None) -> None:
        self.photo_size_max = photo_size_max  # int
        self.video_size_max = video_size_max  # int
        self.file_size_max = file_size_max  # int
        self.video_upload_maxbitrate = video_upload_maxbitrate  # int
        self.disabled = disabled  # flags.0?true
        self.video_preload_large = video_preload_large  # flags.1?true
        self.audio_preload_next = audio_preload_next  # flags.2?true
        self.phonecalls_less_data = phonecalls_less_data  # flags.3?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        disabled = True if flags & (1 << 0) else False
        video_preload_large = True if flags & (1 << 1) else False
        audio_preload_next = True if flags & (1 << 2) else False
        phonecalls_less_data = True if flags & (1 << 3) else False
        photo_size_max = Int.read(data)
        
        video_size_max = Int.read(data)
        
        file_size_max = Int.read(data)
        
        video_upload_maxbitrate = Int.read(data)
        
        return AutoDownloadSettings(photo_size_max=photo_size_max, video_size_max=video_size_max, file_size_max=file_size_max, video_upload_maxbitrate=video_upload_maxbitrate, disabled=disabled, video_preload_large=video_preload_large, audio_preload_next=audio_preload_next, phonecalls_less_data=phonecalls_less_data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.disabled else 0
        flags |= (1 << 1) if self.video_preload_large else 0
        flags |= (1 << 2) if self.audio_preload_next else 0
        flags |= (1 << 3) if self.phonecalls_less_data else 0
        data.write(Int(flags))
        
        data.write(Int(self.photo_size_max))
        
        data.write(Int(self.video_size_max))
        
        data.write(Int(self.file_size_max))
        
        data.write(Int(self.video_upload_maxbitrate))
        
        return data.getvalue()
