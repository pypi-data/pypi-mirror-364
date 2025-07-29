from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class StickerPack(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StickerPack`.

    Details:
        - Layer: ``135``
        - ID: ``0x12b299d4``

    Parameters:
        emoticon: ``str``
        documents: List of ``int`` ``64-bit``
    """

    __slots__: List[str] = ["emoticon", "documents"]

    ID = 0x12b299d4
    QUALNAME = "types.StickerPack"

    def __init__(self, *, emoticon: str, documents: List[int]) -> None:
        self.emoticon = emoticon  # string
        self.documents = documents  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        emoticon = String.read(data)
        
        documents = TLObject.read(data, Long)
        
        return StickerPack(emoticon=emoticon, documents=documents)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.emoticon))
        
        data.write(Vector(self.documents, Long))
        
        return data.getvalue()
