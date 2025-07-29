from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RpcDropAnswer(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x58e4a740``

    Parameters:
        req_msg_id: ``int`` ``64-bit``

    Returns:
        :obj:`RpcDropAnswer <pyeitaa.raw.base.RpcDropAnswer>`
    """

    __slots__: List[str] = ["req_msg_id"]

    ID = 0x58e4a740
    QUALNAME = "functions.RpcDropAnswer"

    def __init__(self, *, req_msg_id: int) -> None:
        self.req_msg_id = req_msg_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        req_msg_id = Long.read(data)
        
        return RpcDropAnswer(req_msg_id=req_msg_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.req_msg_id))
        
        return data.getvalue()
