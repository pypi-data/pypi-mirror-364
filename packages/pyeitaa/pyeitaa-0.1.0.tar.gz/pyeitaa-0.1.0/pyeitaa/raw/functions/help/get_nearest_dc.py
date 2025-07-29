from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetNearestDc(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1fb33026``

    **No parameters required.**

    Returns:
        :obj:`NearestDc <pyeitaa.raw.base.NearestDc>`
    """

    __slots__: List[str] = []

    ID = 0x1fb33026
    QUALNAME = "functions.help.GetNearestDc"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetNearestDc()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
