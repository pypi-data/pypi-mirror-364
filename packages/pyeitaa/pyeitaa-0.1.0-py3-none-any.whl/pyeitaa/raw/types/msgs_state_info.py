from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MsgsStateInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MsgsStateInfo`.

    Details:
        - Layer: ``135``
        - ID: ``0x4deb57d``

    Parameters:
        req_msg_id: ``int`` ``64-bit``
        info: ``bytes``
    """

    __slots__: List[str] = ["req_msg_id", "info"]

    ID = 0x4deb57d
    QUALNAME = "types.MsgsStateInfo"

    def __init__(self, *, req_msg_id: int, info: bytes) -> None:
        self.req_msg_id = req_msg_id  # long
        self.info = info  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        req_msg_id = Long.read(data)
        
        info = Bytes.read(data)
        
        return MsgsStateInfo(req_msg_id=req_msg_id, info=info)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.req_msg_id))
        
        data.write(Bytes(self.info))
        
        return data.getvalue()
