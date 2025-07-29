from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RecentStickersNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.RecentStickers`.

    Details:
        - Layer: ``135``
        - ID: ``0xb17f890``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetRecentStickers <pyeitaa.raw.functions.messages.GetRecentStickers>`
    """

    __slots__: List[str] = []

    ID = 0xb17f890
    QUALNAME = "types.messages.RecentStickersNotModified"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return RecentStickersNotModified()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
