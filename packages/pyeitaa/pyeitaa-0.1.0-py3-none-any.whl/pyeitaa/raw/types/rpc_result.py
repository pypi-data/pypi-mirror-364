from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RpcResult(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RpcResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0xca392ff``

    Parameters:
        req_msg_id: ``int`` ``64-bit``
        result: :obj:`Object <pyeitaa.raw.base.Object>`
    """

    __slots__: List[str] = ["req_msg_id", "result"]

    ID = -0xca392ff
    QUALNAME = "types.RpcResult"

    def __init__(self, *, req_msg_id: int, result: TLObject) -> None:
        self.req_msg_id = req_msg_id  # long
        self.result = result  # Object

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        req_msg_id = Long.read(data)
        
        result = TLObject.read(data)
        
        return RpcResult(req_msg_id=req_msg_id, result=result)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.req_msg_id))
        
        data.write(self.result.write())
        
        return data.getvalue()
