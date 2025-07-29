from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetSplitRanges(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1cff7e08``

    **No parameters required.**

    Returns:
        List of :obj:`MessageRange <pyeitaa.raw.base.MessageRange>`
    """

    __slots__: List[str] = []

    ID = 0x1cff7e08
    QUALNAME = "functions.messages.GetSplitRanges"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetSplitRanges()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
