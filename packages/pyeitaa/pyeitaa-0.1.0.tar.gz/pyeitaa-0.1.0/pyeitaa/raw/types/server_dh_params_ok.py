from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Int128, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ServerDHParamsOk(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ServerDHParams`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2f17f8a4``

    Parameters:
        nonce: ``int`` ``128-bit``
        server_nonce: ``int`` ``128-bit``
        encrypted_answer: ``bytes``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`ReqDHParams <pyeitaa.raw.functions.ReqDHParams>`
            - :obj:`ReqDHParams <pyeitaa.raw.functions.ReqDHParams>`
    """

    __slots__: List[str] = ["nonce", "server_nonce", "encrypted_answer"]

    ID = -0x2f17f8a4
    QUALNAME = "types.ServerDHParamsOk"

    def __init__(self, *, nonce: int, server_nonce: int, encrypted_answer: bytes) -> None:
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.encrypted_answer = encrypted_answer  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        nonce = Int128.read(data)
        
        server_nonce = Int128.read(data)
        
        encrypted_answer = Bytes.read(data)
        
        return ServerDHParamsOk(nonce=nonce, server_nonce=server_nonce, encrypted_answer=encrypted_answer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int128(self.nonce))
        
        data.write(Int128(self.server_nonce))
        
        data.write(Bytes(self.encrypted_answer))
        
        return data.getvalue()
