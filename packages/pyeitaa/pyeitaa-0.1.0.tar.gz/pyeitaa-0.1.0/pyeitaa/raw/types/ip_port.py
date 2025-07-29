from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class IpPort(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.IpPort`.

    Details:
        - Layer: ``135``
        - ID: ``0xd433ad73``

    Parameters:
        ipv4: ``int`` ``32-bit``
        port: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["ipv4", "port"]

    ID = 0xd433ad73
    QUALNAME = "types.IpPort"

    def __init__(self, *, ipv4: int, port: int) -> None:
        self.ipv4 = ipv4  # int
        self.port = port  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        ipv4 = Int.read(data)
        
        port = Int.read(data)
        
        return IpPort(ipv4=ipv4, port=port)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.ipv4))
        
        data.write(Int(self.port))
        
        return data.getvalue()
