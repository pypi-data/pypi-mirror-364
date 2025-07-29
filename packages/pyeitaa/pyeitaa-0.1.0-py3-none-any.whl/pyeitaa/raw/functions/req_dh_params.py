from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Int128, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ReqDHParams(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x28ed1b42``

    Parameters:
        nonce: ``int`` ``128-bit``
        server_nonce: ``int`` ``128-bit``
        p: ``bytes``
        q: ``bytes``
        public_key_fingerprint: ``int`` ``64-bit``
        encrypted_data: ``bytes``

    Returns:
        :obj:`ServerDHParams <pyeitaa.raw.base.ServerDHParams>`
    """

    __slots__: List[str] = ["nonce", "server_nonce", "p", "q", "public_key_fingerprint", "encrypted_data"]

    ID = -0x28ed1b42
    QUALNAME = "functions.ReqDHParams"

    def __init__(self, *, nonce: int, server_nonce: int, p: bytes, q: bytes, public_key_fingerprint: int, encrypted_data: bytes) -> None:
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.p = p  # bytes
        self.q = q  # bytes
        self.public_key_fingerprint = public_key_fingerprint  # long
        self.encrypted_data = encrypted_data  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        nonce = Int128.read(data)
        
        server_nonce = Int128.read(data)
        
        p = Bytes.read(data)
        
        q = Bytes.read(data)
        
        public_key_fingerprint = Long.read(data)
        
        encrypted_data = Bytes.read(data)
        
        return ReqDHParams(nonce=nonce, server_nonce=server_nonce, p=p, q=q, public_key_fingerprint=public_key_fingerprint, encrypted_data=encrypted_data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int128(self.nonce))
        
        data.write(Int128(self.server_nonce))
        
        data.write(Bytes(self.p))
        
        data.write(Bytes(self.q))
        
        data.write(Long(self.public_key_fingerprint))
        
        data.write(Bytes(self.encrypted_data))
        
        return data.getvalue()
