from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class StatsGraphAsync(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StatsGraph`.

    Details:
        - Layer: ``135``
        - ID: ``0x4a27eb2d``

    Parameters:
        token: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.LoadAsyncGraph <pyeitaa.raw.functions.stats.LoadAsyncGraph>`
    """

    __slots__: List[str] = ["token"]

    ID = 0x4a27eb2d
    QUALNAME = "types.StatsGraphAsync"

    def __init__(self, *, token: str) -> None:
        self.token = token  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        token = String.read(data)
        
        return StatsGraphAsync(token=token)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.token))
        
        return data.getvalue()
