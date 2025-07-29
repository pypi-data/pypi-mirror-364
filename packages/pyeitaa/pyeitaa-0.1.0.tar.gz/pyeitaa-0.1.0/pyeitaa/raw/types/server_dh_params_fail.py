from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Int128
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ServerDHParamsFail(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ServerDHParams`.

    Details:
        - Layer: ``135``
        - ID: ``0x79cb045d``

    Parameters:
        nonce: ``int`` ``128-bit``
        server_nonce: ``int`` ``128-bit``
        new_nonce_hash: ``int`` ``128-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`ReqDHParams <pyeitaa.raw.functions.ReqDHParams>`
            - :obj:`ReqDHParams <pyeitaa.raw.functions.ReqDHParams>`
    """

    __slots__: List[str] = ["nonce", "server_nonce", "new_nonce_hash"]

    ID = 0x79cb045d
    QUALNAME = "types.ServerDHParamsFail"

    def __init__(self, *, nonce: int, server_nonce: int, new_nonce_hash: int) -> None:
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.new_nonce_hash = new_nonce_hash  # int128

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        nonce = Int128.read(data)
        
        server_nonce = Int128.read(data)
        
        new_nonce_hash = Int128.read(data)
        
        return ServerDHParamsFail(nonce=nonce, server_nonce=server_nonce, new_nonce_hash=new_nonce_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int128(self.nonce))
        
        data.write(Int128(self.server_nonce))
        
        data.write(Int128(self.new_nonce_hash))
        
        return data.getvalue()
