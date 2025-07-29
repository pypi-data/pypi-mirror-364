from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UploadTheme(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1c3db333``

    Parameters:
        file: :obj:`InputFile <pyeitaa.raw.base.InputFile>`
        file_name: ``str``
        mime_type: ``str``
        thumb (optional): :obj:`InputFile <pyeitaa.raw.base.InputFile>`

    Returns:
        :obj:`Document <pyeitaa.raw.base.Document>`
    """

    __slots__: List[str] = ["file", "file_name", "mime_type", "thumb"]

    ID = 0x1c3db333
    QUALNAME = "functions.account.UploadTheme"

    def __init__(self, *, file: "raw.base.InputFile", file_name: str, mime_type: str, thumb: "raw.base.InputFile" = None) -> None:
        self.file = file  # InputFile
        self.file_name = file_name  # string
        self.mime_type = mime_type  # string
        self.thumb = thumb  # flags.0?InputFile

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        file = TLObject.read(data)
        
        thumb = TLObject.read(data) if flags & (1 << 0) else None
        
        file_name = String.read(data)
        
        mime_type = String.read(data)
        
        return UploadTheme(file=file, file_name=file_name, mime_type=mime_type, thumb=thumb)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.thumb is not None else 0
        data.write(Int(flags))
        
        data.write(self.file.write())
        
        if self.thumb is not None:
            data.write(self.thumb.write())
        
        data.write(String(self.file_name))
        
        data.write(String(self.mime_type))
        
        return data.getvalue()
