from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Int128, Bytes, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResPQ(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ResPQ`.

    Details:
        - Layer: ``135``
        - ID: ``0x5162463``

    Parameters:
        nonce: ``int`` ``128-bit``
        server_nonce: ``int`` ``128-bit``
        pq: ``bytes``
        server_public_key_fingerprints: List of ``int`` ``64-bit``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`ReqPq <pyeitaa.raw.functions.ReqPq>`
            - :obj:`ReqPqMulti <pyeitaa.raw.functions.ReqPqMulti>`
            - :obj:`ReqPqMulti <pyeitaa.raw.functions.ReqPqMulti>`
    """

    __slots__: List[str] = ["nonce", "server_nonce", "pq", "server_public_key_fingerprints"]

    ID = 0x5162463
    QUALNAME = "types.ResPQ"

    def __init__(self, *, nonce: int, server_nonce: int, pq: bytes, server_public_key_fingerprints: List[int]) -> None:
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.pq = pq  # bytes
        self.server_public_key_fingerprints = server_public_key_fingerprints  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        nonce = Int128.read(data)
        
        server_nonce = Int128.read(data)
        
        pq = Bytes.read(data)
        
        server_public_key_fingerprints = TLObject.read(data, Long)
        
        return ResPQ(nonce=nonce, server_nonce=server_nonce, pq=pq, server_public_key_fingerprints=server_public_key_fingerprints)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int128(self.nonce))
        
        data.write(Int128(self.server_nonce))
        
        data.write(Bytes(self.pq))
        
        data.write(Vector(self.server_public_key_fingerprints, Long))
        
        return data.getvalue()
