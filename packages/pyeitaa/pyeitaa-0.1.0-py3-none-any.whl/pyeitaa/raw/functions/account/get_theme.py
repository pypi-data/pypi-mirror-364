from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetTheme(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x72628bd5``

    Parameters:
        format: ``str``
        theme: :obj:`InputTheme <pyeitaa.raw.base.InputTheme>`
        document_id: ``int`` ``64-bit``

    Returns:
        :obj:`Theme <pyeitaa.raw.base.Theme>`
    """

    __slots__: List[str] = ["format", "theme", "document_id"]

    ID = -0x72628bd5
    QUALNAME = "functions.account.GetTheme"

    def __init__(self, *, format: str, theme: "raw.base.InputTheme", document_id: int) -> None:
        self.format = format  # string
        self.theme = theme  # InputTheme
        self.document_id = document_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        format = String.read(data)
        
        theme = TLObject.read(data)
        
        document_id = Long.read(data)
        
        return GetTheme(format=format, theme=theme, document_id=document_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.format))
        
        data.write(self.theme.write())
        
        data.write(Long(self.document_id))
        
        return data.getvalue()
