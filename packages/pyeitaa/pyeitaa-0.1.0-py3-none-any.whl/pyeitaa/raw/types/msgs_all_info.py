from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MsgsAllInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MsgsAllInfo`.

    Details:
        - Layer: ``135``
        - ID: ``-0x733f2ecf``

    Parameters:
        msg_ids: List of ``int`` ``64-bit``
        info: ``bytes``
    """

    __slots__: List[str] = ["msg_ids", "info"]

    ID = -0x733f2ecf
    QUALNAME = "types.MsgsAllInfo"

    def __init__(self, *, msg_ids: List[int], info: bytes) -> None:
        self.msg_ids = msg_ids  # Vector<long>
        self.info = info  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        msg_ids = TLObject.read(data, Long)
        
        info = Bytes.read(data)
        
        return MsgsAllInfo(msg_ids=msg_ids, info=info)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.msg_ids, Long))
        
        data.write(Bytes(self.info))
        
        return data.getvalue()
