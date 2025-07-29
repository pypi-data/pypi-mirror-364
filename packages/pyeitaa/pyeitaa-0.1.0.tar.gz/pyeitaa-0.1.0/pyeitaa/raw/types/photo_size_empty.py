from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PhotoSizeEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhotoSize`.

    Details:
        - Layer: ``135``
        - ID: ``0xe17e23c``

    Parameters:
        type: ``str``
    """

    __slots__: List[str] = ["type"]

    ID = 0xe17e23c
    QUALNAME = "types.PhotoSizeEmpty"

    def __init__(self, *, type: str) -> None:
        self.type = type  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = String.read(data)
        
        return PhotoSizeEmpty(type=type)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.type))
        
        return data.getvalue()
