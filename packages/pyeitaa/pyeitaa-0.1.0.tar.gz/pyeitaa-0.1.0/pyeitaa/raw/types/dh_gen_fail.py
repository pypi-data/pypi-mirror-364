from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Int128
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DhGenFail(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SetClientDHParamsAnswer`.

    Details:
        - Layer: ``135``
        - ID: ``-0x596251fe``

    Parameters:
        nonce: ``int`` ``128-bit``
        server_nonce: ``int`` ``128-bit``
        new_nonce_hash3: ``int`` ``128-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`SetClientDHParams <pyeitaa.raw.functions.SetClientDHParams>`
            - :obj:`SetClientDHParams <pyeitaa.raw.functions.SetClientDHParams>`
    """

    __slots__: List[str] = ["nonce", "server_nonce", "new_nonce_hash3"]

    ID = -0x596251fe
    QUALNAME = "types.DhGenFail"

    def __init__(self, *, nonce: int, server_nonce: int, new_nonce_hash3: int) -> None:
        self.nonce = nonce  # int128
        self.server_nonce = server_nonce  # int128
        self.new_nonce_hash3 = new_nonce_hash3  # int128

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        nonce = Int128.read(data)
        
        server_nonce = Int128.read(data)
        
        new_nonce_hash3 = Int128.read(data)
        
        return DhGenFail(nonce=nonce, server_nonce=server_nonce, new_nonce_hash3=new_nonce_hash3)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int128(self.nonce))
        
        data.write(Int128(self.server_nonce))
        
        data.write(Int128(self.new_nonce_hash3))
        
        return data.getvalue()
