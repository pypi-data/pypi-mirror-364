from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetSupport(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6320f733``

    **No parameters required.**

    Returns:
        :obj:`help.Support <pyeitaa.raw.base.help.Support>`
    """

    __slots__: List[str] = []

    ID = -0x6320f733
    QUALNAME = "functions.help.GetSupport"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetSupport()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
