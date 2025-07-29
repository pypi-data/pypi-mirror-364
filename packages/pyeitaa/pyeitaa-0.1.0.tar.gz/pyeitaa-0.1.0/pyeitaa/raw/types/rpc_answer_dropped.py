from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RpcAnswerDropped(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RpcDropAnswer`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5bc52749``

    Parameters:
        msg_id: ``int`` ``64-bit``
        seq_no: ``int`` ``32-bit``
        bytes: ``int`` ``32-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`RpcDropAnswer <pyeitaa.raw.functions.RpcDropAnswer>`
            - :obj:`RpcDropAnswer <pyeitaa.raw.functions.RpcDropAnswer>`
    """

    __slots__: List[str] = ["msg_id", "seq_no", "bytes"]

    ID = -0x5bc52749
    QUALNAME = "types.RpcAnswerDropped"

    def __init__(self, *, msg_id: int, seq_no: int, bytes: int) -> None:
        self.msg_id = msg_id  # long
        self.seq_no = seq_no  # int
        self.bytes = bytes  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        msg_id = Long.read(data)
        
        seq_no = Int.read(data)
        
        bytes = Int.read(data)
        
        return RpcAnswerDropped(msg_id=msg_id, seq_no=seq_no, bytes=bytes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.msg_id))
        
        data.write(Int(self.seq_no))
        
        data.write(Int(self.bytes))
        
        return data.getvalue()
