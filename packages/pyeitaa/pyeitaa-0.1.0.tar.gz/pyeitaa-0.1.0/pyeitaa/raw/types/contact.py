from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bool
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class Contact(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Contact`.

    Details:
        - Layer: ``135``
        - ID: ``0x145ade0b``

    Parameters:
        user_id: ``int`` ``64-bit``
        mutual: ``bool``
    """

    __slots__: List[str] = ["user_id", "mutual"]

    ID = 0x145ade0b
    QUALNAME = "types.Contact"

    def __init__(self, *, user_id: int, mutual: bool) -> None:
        self.user_id = user_id  # long
        self.mutual = mutual  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        mutual = Bool.read(data)
        
        return Contact(user_id=user_id, mutual=mutual)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Bool(self.mutual))
        
        return data.getvalue()
