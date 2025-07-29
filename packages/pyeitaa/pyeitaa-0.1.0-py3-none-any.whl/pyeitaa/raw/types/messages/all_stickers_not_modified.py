from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class AllStickersNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.AllStickers`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1799fd3d``

    **No parameters required.**

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAllStickers <pyeitaa.raw.functions.messages.GetAllStickers>`
            - :obj:`messages.GetMaskStickers <pyeitaa.raw.functions.messages.GetMaskStickers>`
    """

    __slots__: List[str] = []

    ID = -0x1799fd3d
    QUALNAME = "types.messages.AllStickersNotModified"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return AllStickersNotModified()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
