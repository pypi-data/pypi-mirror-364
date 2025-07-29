from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputUser(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputUser`.

    Details:
        - Layer: ``135``
        - ID: ``-0xdeea73a``

    Parameters:
        user_id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["user_id", "access_hash"]

    ID = -0xdeea73a
    QUALNAME = "types.InputUser"

    def __init__(self, *, user_id: int, access_hash: int) -> None:
        self.user_id = user_id  # long
        self.access_hash = access_hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        access_hash = Long.read(data)
        
        return InputUser(user_id=user_id, access_hash=access_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Long(self.access_hash))
        
        return data.getvalue()
