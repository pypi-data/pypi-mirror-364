from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Int128, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ServerDHInnerData(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ServerDHInnerData`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4a76f246``

    Parameters:
        nonce: ``int`` ``128-bit``
        server_nonce: ``int`` ``128-bit``
        g: ``int`` ``32-bit``
        dh_prime: ``bytes``
        g_a: ``bytes``
        server_time: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["nonce", "server_nonce", "g", "dh_prime", "g_a", "server_time"]

    ID = -0x4a76f246
    QUALNAME = "types.ServerDHInnerData"

    def __init__(self, *, nonce: int, server_nonce: int, g: int, dh_prime: bytes, g_a: bytes, server_time: int) -> None:
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.g = g  # int
        self.dh_prime = dh_prime  # bytes
        self.g_a = g_a  # bytes
        self.server_time = server_time  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        nonce = Int128.read(data)
        
        server_nonce = Int128.read(data)
        
        g = Int.read(data)
        
        dh_prime = Bytes.read(data)
        
        g_a = Bytes.read(data)
        
        server_time = Int.read(data)
        
        return ServerDHInnerData(nonce=nonce, server_nonce=server_nonce, g=g, dh_prime=dh_prime, g_a=g_a, server_time=server_time)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int128(self.nonce))
        
        data.write(Int128(self.server_nonce))
        
        data.write(Int(self.g))
        
        data.write(Bytes(self.dh_prime))
        
        data.write(Bytes(self.g_a))
        
        data.write(Int(self.server_time))
        
        return data.getvalue()
