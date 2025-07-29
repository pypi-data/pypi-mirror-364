from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PageBlockUnsupported(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``0x13567e8a``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = 0x13567e8a
    QUALNAME = "types.PageBlockUnsupported"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return PageBlockUnsupported()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
