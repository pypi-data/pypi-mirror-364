from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Int128, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SetClientDHParams(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xafba0e1``

    Parameters:
        nonce: ``int`` ``128-bit``
        server_nonce: ``int`` ``128-bit``
        encrypted_data: ``bytes``

    Returns:
        :obj:`SetClientDHParamsAnswer <pyeitaa.raw.base.SetClientDHParamsAnswer>`
    """

    __slots__: List[str] = ["nonce", "server_nonce", "encrypted_data"]

    ID = -0xafba0e1
    QUALNAME = "functions.SetClientDHParams"

    def __init__(self, *, nonce: int, server_nonce: int, encrypted_data: bytes) -> None:
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.encrypted_data = encrypted_data  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        nonce = Int128.read(data)
        
        server_nonce = Int128.read(data)
        
        encrypted_data = Bytes.read(data)
        
        return SetClientDHParams(nonce=nonce, server_nonce=server_nonce, encrypted_data=encrypted_data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int128(self.nonce))
        
        data.write(Int128(self.server_nonce))
        
        data.write(Bytes(self.encrypted_data))
        
        return data.getvalue()
