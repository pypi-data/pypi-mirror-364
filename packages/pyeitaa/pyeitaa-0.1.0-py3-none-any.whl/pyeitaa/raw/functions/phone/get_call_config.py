from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetCallConfig(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x55451fa9``

    **No parameters required.**

    Returns:
        :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
    """

    __slots__: List[str] = []

    ID = 0x55451fa9
    QUALNAME = "functions.phone.GetCallConfig"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetCallConfig()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
