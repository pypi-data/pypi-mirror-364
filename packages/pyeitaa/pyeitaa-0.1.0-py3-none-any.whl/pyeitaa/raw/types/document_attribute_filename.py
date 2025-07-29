from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DocumentAttributeFilename(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DocumentAttribute`.

    Details:
        - Layer: ``135``
        - ID: ``0x15590068``

    Parameters:
        file_name: ``str``
    """

    __slots__: List[str] = ["file_name"]

    ID = 0x15590068
    QUALNAME = "types.DocumentAttributeFilename"

    def __init__(self, *, file_name: str) -> None:
        self.file_name = file_name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        file_name = String.read(data)
        
        return DocumentAttributeFilename(file_name=file_name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.file_name))
        
        return data.getvalue()
