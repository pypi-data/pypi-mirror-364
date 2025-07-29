from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Int128
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ReqPq(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x60469778``

    Parameters:
        nonce: ``int`` ``128-bit``

    Returns:
        :obj:`ResPQ <pyeitaa.raw.base.ResPQ>`
    """

    __slots__: List[str] = ["nonce"]

    ID = 0x60469778
    QUALNAME = "functions.ReqPq"

    def __init__(self, *, nonce: int) -> None:
        self.nonce = nonce  # int128

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        nonce = Int128.read(data)
        
        return ReqPq(nonce=nonce)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int128(self.nonce))
        
        return data.getvalue()
