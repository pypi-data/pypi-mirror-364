from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class IpPortSecret(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.IpPort`.

    Details:
        - Layer: ``135``
        - ID: ``0x37982646``

    Parameters:
        ipv4: ``int`` ``32-bit``
        port: ``int`` ``32-bit``
        secret: ``bytes``
    """

    __slots__: List[str] = ["ipv4", "port", "secret"]

    ID = 0x37982646
    QUALNAME = "types.IpPortSecret"

    def __init__(self, *, ipv4: int, port: int, secret: bytes) -> None:
        self.ipv4 = ipv4  # int
        self.port = port  # int
        self.secret = secret  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        ipv4 = Int.read(data)
        
        port = Int.read(data)
        
        secret = Bytes.read(data)
        
        return IpPortSecret(ipv4=ipv4, port=port, secret=secret)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.ipv4))
        
        data.write(Int(self.port))
        
        data.write(Bytes(self.secret))
        
        return data.getvalue()
