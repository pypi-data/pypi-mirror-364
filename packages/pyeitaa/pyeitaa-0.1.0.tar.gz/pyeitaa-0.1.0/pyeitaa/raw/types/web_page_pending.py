from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class WebPagePending(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.WebPage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3a7925e4``

    Parameters:
        id: ``int`` ``64-bit``
        date: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPage <pyeitaa.raw.functions.messages.GetWebPage>`
    """

    __slots__: List[str] = ["id", "date"]

    ID = -0x3a7925e4
    QUALNAME = "types.WebPagePending"

    def __init__(self, *, id: int, date: int) -> None:
        self.id = id  # long
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        date = Int.read(data)
        
        return WebPagePending(id=id, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Int(self.date))
        
        return data.getvalue()
