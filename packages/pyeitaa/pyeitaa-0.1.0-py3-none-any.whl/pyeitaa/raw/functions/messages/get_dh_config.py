from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetDhConfig(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x26cf8950``

    Parameters:
        version: ``int`` ``32-bit``
        random_length: ``int`` ``32-bit``

    Returns:
        :obj:`messages.DhConfig <pyeitaa.raw.base.messages.DhConfig>`
    """

    __slots__: List[str] = ["version", "random_length"]

    ID = 0x26cf8950
    QUALNAME = "functions.messages.GetDhConfig"

    def __init__(self, *, version: int, random_length: int) -> None:
        self.version = version  # int
        self.random_length = random_length  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        version = Int.read(data)
        
        random_length = Int.read(data)
        
        return GetDhConfig(version=version, random_length=random_length)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.version))
        
        data.write(Int(self.random_length))
        
        return data.getvalue()
