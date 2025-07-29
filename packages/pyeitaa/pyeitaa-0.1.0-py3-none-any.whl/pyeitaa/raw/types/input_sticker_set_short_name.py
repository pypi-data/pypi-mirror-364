from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputStickerSetShortName(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputStickerSet`.

    Details:
        - Layer: ``135``
        - ID: ``-0x79e33760``

    Parameters:
        short_name: ``str``
    """

    __slots__: List[str] = ["short_name"]

    ID = -0x79e33760
    QUALNAME = "types.InputStickerSetShortName"

    def __init__(self, *, short_name: str) -> None:
        self.short_name = short_name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        short_name = String.read(data)
        
        return InputStickerSetShortName(short_name=short_name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.short_name))
        
        return data.getvalue()
