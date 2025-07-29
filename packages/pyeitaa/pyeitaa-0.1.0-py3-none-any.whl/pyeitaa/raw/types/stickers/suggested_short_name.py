from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SuggestedShortName(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.stickers.SuggestedShortName`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7a015fc1``

    Parameters:
        short_name: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stickers.SuggestShortName <pyeitaa.raw.functions.stickers.SuggestShortName>`
    """

    __slots__: List[str] = ["short_name"]

    ID = -0x7a015fc1
    QUALNAME = "types.stickers.SuggestedShortName"

    def __init__(self, *, short_name: str) -> None:
        self.short_name = short_name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        short_name = String.read(data)
        
        return SuggestedShortName(short_name=short_name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.short_name))
        
        return data.getvalue()
