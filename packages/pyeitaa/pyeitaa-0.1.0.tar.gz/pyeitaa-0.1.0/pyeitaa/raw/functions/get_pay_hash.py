from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetPayHash(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x21524151``

    Parameters:
        flag: ``int`` ``32-bit``
        msg_id: ``int`` ``32-bit``
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`

    Returns:
        :obj:`UserPayHash <pyeitaa.raw.base.UserPayHash>`
    """

    __slots__: List[str] = ["flag", "msg_id", "peer"]

    ID = -0x21524151
    QUALNAME = "functions.GetPayHash"

    def __init__(self, *, flag: int, msg_id: int, peer: "raw.base.Peer") -> None:
        self.flag = flag  # int
        self.msg_id = msg_id  # int
        self.peer = peer  # Peer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        flag = Int.read(data)
        
        msg_id = Int.read(data)
        
        peer = TLObject.read(data)
        
        return GetPayHash(flag=flag, msg_id=msg_id, peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.flag))
        
        data.write(Int(self.msg_id))
        
        data.write(self.peer.write())
        
        return data.getvalue()
