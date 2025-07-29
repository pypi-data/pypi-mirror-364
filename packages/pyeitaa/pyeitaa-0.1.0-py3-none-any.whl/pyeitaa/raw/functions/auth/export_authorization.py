from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ExportAuthorization(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1a400033``

    Parameters:
        dc_id: ``int`` ``32-bit``

    Returns:
        :obj:`auth.ExportedAuthorization <pyeitaa.raw.base.auth.ExportedAuthorization>`
    """

    __slots__: List[str] = ["dc_id"]

    ID = -0x1a400033
    QUALNAME = "functions.auth.ExportAuthorization"

    def __init__(self, *, dc_id: int) -> None:
        self.dc_id = dc_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        dc_id = Int.read(data)
        
        return ExportAuthorization(dc_id=dc_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.dc_id))
        
        return data.getvalue()
