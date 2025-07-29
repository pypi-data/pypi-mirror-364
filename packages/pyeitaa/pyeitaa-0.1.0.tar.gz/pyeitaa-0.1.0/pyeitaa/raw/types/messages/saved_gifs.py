from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SavedGifs(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.SavedGifs`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7b5fd5f3``

    Parameters:
        hash: ``int`` ``64-bit``
        gifs: List of :obj:`Document <pyeitaa.raw.base.Document>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetSavedGifs <pyeitaa.raw.functions.messages.GetSavedGifs>`
    """

    __slots__: List[str] = ["hash", "gifs"]

    ID = -0x7b5fd5f3
    QUALNAME = "types.messages.SavedGifs"

    def __init__(self, *, hash: int, gifs: List["raw.base.Document"]) -> None:
        self.hash = hash  # long
        self.gifs = gifs  # Vector<Document>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        gifs = TLObject.read(data)
        
        return SavedGifs(hash=hash, gifs=gifs)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        data.write(Vector(self.gifs))
        
        return data.getvalue()
