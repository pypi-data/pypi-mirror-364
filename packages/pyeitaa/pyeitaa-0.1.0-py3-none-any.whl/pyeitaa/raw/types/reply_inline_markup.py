from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ReplyInlineMarkup(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ReplyMarkup`.

    Details:
        - Layer: ``135``
        - ID: ``0x48a30254``

    Parameters:
        rows: List of :obj:`KeyboardButtonRow <pyeitaa.raw.base.KeyboardButtonRow>`
    """

    __slots__: List[str] = ["rows"]

    ID = 0x48a30254
    QUALNAME = "types.ReplyInlineMarkup"

    def __init__(self, *, rows: List["raw.base.KeyboardButtonRow"]) -> None:
        self.rows = rows  # Vector<KeyboardButtonRow>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        rows = TLObject.read(data)
        
        return ReplyInlineMarkup(rows=rows)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.rows))
        
        return data.getvalue()
