from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class TextConcat(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RichText`.

    Details:
        - Layer: ``135``
        - ID: ``0x7e6260d7``

    Parameters:
        texts: List of :obj:`RichText <pyeitaa.raw.base.RichText>`
    """

    __slots__: List[str] = ["texts"]

    ID = 0x7e6260d7
    QUALNAME = "types.TextConcat"

    def __init__(self, *, texts: List["raw.base.RichText"]) -> None:
        self.texts = texts  # Vector<RichText>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        texts = TLObject.read(data)
        
        return TextConcat(texts=texts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.texts))
        
        return data.getvalue()
