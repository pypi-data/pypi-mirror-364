from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Int128, Int256, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PQInnerDataDc(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PQInnerData`.

    Details:
        - Layer: ``135``
        - ID: ``-0x560aa06b``

    Parameters:
        pq: ``bytes``
        p: ``bytes``
        q: ``bytes``
        nonce: ``int`` ``128-bit``
        server_nonce: ``int`` ``128-bit``
        new_nonce: ``int`` ``256-bit``
        dc: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["pq", "p", "q", "nonce", "server_nonce", "new_nonce", "dc"]

    ID = -0x560aa06b
    QUALNAME = "types.PQInnerDataDc"

    def __init__(self, *, pq: bytes, p: bytes, q: bytes, nonce: int, server_nonce: int, new_nonce: int, dc: int) -> None:
        self.pq = pq  # bytes
        self.p = p  # bytes
        self.q = q  # bytes
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.new_nonce = new_nonce  # int256
        self.dc = dc  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        pq = Bytes.read(data)
        
        p = Bytes.read(data)
        
        q = Bytes.read(data)
        
        nonce = Int128.read(data)
        
        server_nonce = Int128.read(data)
        
        new_nonce = Int256.read(data)
        
        dc = Int.read(data)
        
        return PQInnerDataDc(pq=pq, p=p, q=q, nonce=nonce, server_nonce=server_nonce, new_nonce=new_nonce, dc=dc)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.pq))
        
        data.write(Bytes(self.p))
        
        data.write(Bytes(self.q))
        
        data.write(Int128(self.nonce))
        
        data.write(Int128(self.server_nonce))
        
        data.write(Int256(self.new_nonce))
        
        data.write(Int(self.dc))
        
        return data.getvalue()
