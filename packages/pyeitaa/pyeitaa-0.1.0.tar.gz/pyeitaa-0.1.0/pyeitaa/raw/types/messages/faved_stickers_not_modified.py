from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class FavedStickersNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.FavedStickers`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6170592d``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetFavedStickers <pyeitaa.raw.functions.messages.GetFavedStickers>`
    """

    __slots__: List[str] = []

    ID = -0x6170592d
    QUALNAME = "types.messages.FavedStickersNotModified"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return FavedStickersNotModified()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
