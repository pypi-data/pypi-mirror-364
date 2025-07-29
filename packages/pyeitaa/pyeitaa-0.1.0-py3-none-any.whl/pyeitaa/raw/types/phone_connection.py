from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PhoneConnection(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhoneConnection`.

    Details:
        - Layer: ``135``
        - ID: ``-0x62b3e840``

    Parameters:
        id: ``int`` ``64-bit``
        ip: ``str``
        ipv6: ``str``
        port: ``int`` ``32-bit``
        peer_tag: ``bytes``
    """

    __slots__: List[str] = ["id", "ip", "ipv6", "port", "peer_tag"]

    ID = -0x62b3e840
    QUALNAME = "types.PhoneConnection"

    def __init__(self, *, id: int, ip: str, ipv6: str, port: int, peer_tag: bytes) -> None:
        self.id = id  # long
        self.ip = ip  # string
        self.ipv6 = ipv6  # string
        self.port = port  # int
        self.peer_tag = peer_tag  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        ip = String.read(data)
        
        ipv6 = String.read(data)
        
        port = Int.read(data)
        
        peer_tag = Bytes.read(data)
        
        return PhoneConnection(id=id, ip=ip, ipv6=ipv6, port=port, peer_tag=peer_tag)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(String(self.ip))
        
        data.write(String(self.ipv6))
        
        data.write(Int(self.port))
        
        data.write(Bytes(self.peer_tag))
        
        return data.getvalue()
