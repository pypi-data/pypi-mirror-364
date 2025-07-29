from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UnregisterDevice(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x6a0d3206``

    Parameters:
        token_type: ``int`` ``32-bit``
        token: ``str``
        other_uids: List of ``int`` ``64-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["token_type", "token", "other_uids"]

    ID = 0x6a0d3206
    QUALNAME = "functions.account.UnregisterDevice"

    def __init__(self, *, token_type: int, token: str, other_uids: List[int]) -> None:
        self.token_type = token_type  # int
        self.token = token  # string
        self.other_uids = other_uids  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        token_type = Int.read(data)
        
        token = String.read(data)
        
        other_uids = TLObject.read(data, Long)
        
        return UnregisterDevice(token_type=token_type, token=token, other_uids=other_uids)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.token_type))
        
        data.write(String(self.token))
        
        data.write(Vector(self.other_uids, Long))
        
        return data.getvalue()
