from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SearchCounter(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.SearchCounter`.

    Details:
        - Layer: ``135``
        - ID: ``-0x17bb1401``

    Parameters:
        filter: :obj:`MessagesFilter <pyeitaa.raw.base.MessagesFilter>`
        count: ``int`` ``32-bit``
        inexact (optional): ``bool``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetSearchCounters <pyeitaa.raw.functions.messages.GetSearchCounters>`
    """

    __slots__: List[str] = ["filter", "count", "inexact"]

    ID = -0x17bb1401
    QUALNAME = "types.messages.SearchCounter"

    def __init__(self, *, filter: "raw.base.MessagesFilter", count: int, inexact: Optional[bool] = None) -> None:
        self.filter = filter  # MessagesFilter
        self.count = count  # int
        self.inexact = inexact  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        inexact = True if flags & (1 << 1) else False
        filter = TLObject.read(data)
        
        count = Int.read(data)
        
        return SearchCounter(filter=filter, count=count, inexact=inexact)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.inexact else 0
        data.write(Int(flags))
        
        data.write(self.filter.write())
        
        data.write(Int(self.count))
        
        return data.getvalue()
