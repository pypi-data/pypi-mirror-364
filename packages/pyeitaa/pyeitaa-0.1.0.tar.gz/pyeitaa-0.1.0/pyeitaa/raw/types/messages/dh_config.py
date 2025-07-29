from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DhConfig(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.DhConfig`.

    Details:
        - Layer: ``135``
        - ID: ``0x2c221edd``

    Parameters:
        g: ``int`` ``32-bit``
        p: ``bytes``
        version: ``int`` ``32-bit``
        random: ``bytes``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDhConfig <pyeitaa.raw.functions.messages.GetDhConfig>`
    """

    __slots__: List[str] = ["g", "p", "version", "random"]

    ID = 0x2c221edd
    QUALNAME = "types.messages.DhConfig"

    def __init__(self, *, g: int, p: bytes, version: int, random: bytes) -> None:
        self.g = g  # int
        self.p = p  # bytes
        self.version = version  # int
        self.random = random  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        g = Int.read(data)
        
        p = Bytes.read(data)
        
        version = Int.read(data)
        
        random = Bytes.read(data)
        
        return DhConfig(g=g, p=p, version=version, random=random)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.g))
        
        data.write(Bytes(self.p))
        
        data.write(Int(self.version))
        
        data.write(Bytes(self.random))
        
        return data.getvalue()
