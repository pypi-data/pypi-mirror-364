from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PeerUser(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Peer`.

    Details:
        - Layer: ``135``
        - ID: ``0x59511722``

    Parameters:
        user_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["user_id"]

    ID = 0x59511722
    QUALNAME = "types.PeerUser"

    def __init__(self, *, user_id: int) -> None:
        self.user_id = user_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        return PeerUser(user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        return data.getvalue()
