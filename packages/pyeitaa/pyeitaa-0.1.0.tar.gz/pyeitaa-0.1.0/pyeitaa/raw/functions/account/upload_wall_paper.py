from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UploadWallPaper(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x227ac99f``

    Parameters:
        file: :obj:`InputFile <pyeitaa.raw.base.InputFile>`
        mime_type: ``str``
        settings: :obj:`WallPaperSettings <pyeitaa.raw.base.WallPaperSettings>`

    Returns:
        :obj:`WallPaper <pyeitaa.raw.base.WallPaper>`
    """

    __slots__: List[str] = ["file", "mime_type", "settings"]

    ID = -0x227ac99f
    QUALNAME = "functions.account.UploadWallPaper"

    def __init__(self, *, file: "raw.base.InputFile", mime_type: str, settings: "raw.base.WallPaperSettings") -> None:
        self.file = file  # InputFile
        self.mime_type = mime_type  # string
        self.settings = settings  # WallPaperSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        file = TLObject.read(data)
        
        mime_type = String.read(data)
        
        settings = TLObject.read(data)
        
        return UploadWallPaper(file=file, mime_type=mime_type, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.file.write())
        
        data.write(String(self.mime_type))
        
        data.write(self.settings.write())
        
        return data.getvalue()
