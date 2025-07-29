from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class StatsGraphError(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StatsGraph`.

    Details:
        - Layer: ``135``
        - ID: ``-0x412367de``

    Parameters:
        error: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.LoadAsyncGraph <pyeitaa.raw.functions.stats.LoadAsyncGraph>`
    """

    __slots__: List[str] = ["error"]

    ID = -0x412367de
    QUALNAME = "types.StatsGraphError"

    def __init__(self, *, error: str) -> None:
        self.error = error  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        error = String.read(data)
        
        return StatsGraphError(error=error)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.error))
        
        return data.getvalue()
