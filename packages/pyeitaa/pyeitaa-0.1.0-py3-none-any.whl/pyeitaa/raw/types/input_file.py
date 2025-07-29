from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputFile(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputFile`.

    Details:
        - Layer: ``135``
        - ID: ``-0xad00d81``

    Parameters:
        id: ``int`` ``64-bit``
        parts: ``int`` ``32-bit``
        name: ``str``
        md5_checksum: ``str``
    """

    __slots__: List[str] = ["id", "parts", "name", "md5_checksum"]

    ID = -0xad00d81
    QUALNAME = "types.InputFile"

    def __init__(self, *, id: int, parts: int, name: str, md5_checksum: str) -> None:
        self.id = id  # long
        self.parts = parts  # int
        self.name = name  # string
        self.md5_checksum = md5_checksum  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        parts = Int.read(data)
        
        name = String.read(data)
        
        md5_checksum = String.read(data)
        
        return InputFile(id=id, parts=parts, name=name, md5_checksum=md5_checksum)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Int(self.parts))
        
        data.write(String(self.name))
        
        data.write(String(self.md5_checksum))
        
        return data.getvalue()
