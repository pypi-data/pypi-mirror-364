from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetSupportName(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2c9f18d4``

    **No parameters required.**

    Returns:
        :obj:`help.SupportName <pyeitaa.raw.base.help.SupportName>`
    """

    __slots__: List[str] = []

    ID = -0x2c9f18d4
    QUALNAME = "functions.help.GetSupportName"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetSupportName()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
