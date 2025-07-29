from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputFileBig(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputFile`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5b0f44b``

    Parameters:
        id: ``int`` ``64-bit``
        parts: ``int`` ``32-bit``
        name: ``str``
    """

    __slots__: List[str] = ["id", "parts", "name"]

    ID = -0x5b0f44b
    QUALNAME = "types.InputFileBig"

    def __init__(self, *, id: int, parts: int, name: str) -> None:
        self.id = id  # long
        self.parts = parts  # int
        self.name = name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        parts = Int.read(data)
        
        name = String.read(data)
        
        return InputFileBig(id=id, parts=parts, name=name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Int(self.parts))
        
        data.write(String(self.name))
        
        return data.getvalue()
