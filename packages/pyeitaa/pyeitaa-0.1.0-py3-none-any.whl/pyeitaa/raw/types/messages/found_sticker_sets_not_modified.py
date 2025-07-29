from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class FoundStickerSetsNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.FoundStickerSets`.

    Details:
        - Layer: ``135``
        - ID: ``0xd54b65d``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.SearchStickerSets <pyeitaa.raw.functions.messages.SearchStickerSets>`
    """

    __slots__: List[str] = []

    ID = 0xd54b65d
    QUALNAME = "types.messages.FoundStickerSetsNotModified"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return FoundStickerSetsNotModified()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
