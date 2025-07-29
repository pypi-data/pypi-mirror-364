from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetPassportConfig(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x399e52f8``

    Parameters:
        hash: ``int`` ``32-bit``

    Returns:
        :obj:`help.PassportConfig <pyeitaa.raw.base.help.PassportConfig>`
    """

    __slots__: List[str] = ["hash"]

    ID = -0x399e52f8
    QUALNAME = "functions.help.GetPassportConfig"

    def __init__(self, *, hash: int) -> None:
        self.hash = hash  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Int.read(data)
        
        return GetPassportConfig(hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.hash))
        
        return data.getvalue()
