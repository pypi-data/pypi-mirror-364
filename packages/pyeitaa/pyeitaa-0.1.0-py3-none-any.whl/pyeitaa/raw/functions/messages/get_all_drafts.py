from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetAllDrafts(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x6a3f8d65``

    **No parameters required.**

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = []

    ID = 0x6a3f8d65
    QUALNAME = "functions.messages.GetAllDrafts"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetAllDrafts()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
