from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageStats(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.stats.MessageStats`.

    Details:
        - Layer: ``135``
        - ID: ``-0x76660d6b``

    Parameters:
        views_graph: :obj:`StatsGraph <pyeitaa.raw.base.StatsGraph>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.GetMessageStats <pyeitaa.raw.functions.stats.GetMessageStats>`
    """

    __slots__: List[str] = ["views_graph"]

    ID = -0x76660d6b
    QUALNAME = "types.stats.MessageStats"

    def __init__(self, *, views_graph: "raw.base.StatsGraph") -> None:
        self.views_graph = views_graph  # StatsGraph

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        views_graph = TLObject.read(data)
        
        return MessageStats(views_graph=views_graph)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.views_graph.write())
        
        return data.getvalue()
