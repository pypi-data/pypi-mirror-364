from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Int128, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ClientDHInnerData(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ClientDHInnerData`.

    Details:
        - Layer: ``135``
        - ID: ``0x6643b654``

    Parameters:
        nonce: ``int`` ``128-bit``
        server_nonce: ``int`` ``128-bit``
        retry_id: ``int`` ``64-bit``
        g_b: ``bytes``
    """

    __slots__: List[str] = ["nonce", "server_nonce", "retry_id", "g_b"]

    ID = 0x6643b654
    QUALNAME = "types.ClientDHInnerData"

    def __init__(self, *, nonce: int, server_nonce: int, retry_id: int, g_b: bytes) -> None:
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.retry_id = retry_id  # long
        self.g_b = g_b  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        nonce = Int128.read(data)
        
        server_nonce = Int128.read(data)
        
        retry_id = Long.read(data)
        
        g_b = Bytes.read(data)
        
        return ClientDHInnerData(nonce=nonce, server_nonce=server_nonce, retry_id=retry_id, g_b=g_b)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int128(self.nonce))
        
        data.write(Int128(self.server_nonce))
        
        data.write(Long(self.retry_id))
        
        data.write(Bytes(self.g_b))
        
        return data.getvalue()
