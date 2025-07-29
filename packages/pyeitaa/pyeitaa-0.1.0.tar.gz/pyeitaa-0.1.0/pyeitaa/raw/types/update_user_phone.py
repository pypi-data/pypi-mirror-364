from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateUserPhone(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x5492a13``

    Parameters:
        user_id: ``int`` ``64-bit``
        phone: ``str``
    """

    __slots__: List[str] = ["user_id", "phone"]

    ID = 0x5492a13
    QUALNAME = "types.UpdateUserPhone"

    def __init__(self, *, user_id: int, phone: str) -> None:
        self.user_id = user_id  # long
        self.phone = phone  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        phone = String.read(data)
        
        return UpdateUserPhone(user_id=user_id, phone=phone)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(String(self.phone))
        
        return data.getvalue()
