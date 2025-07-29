from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateUserStatus(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1a420722``

    Parameters:
        user_id: ``int`` ``64-bit``
        status: :obj:`UserStatus <pyeitaa.raw.base.UserStatus>`
    """

    __slots__: List[str] = ["user_id", "status"]

    ID = -0x1a420722
    QUALNAME = "types.UpdateUserStatus"

    def __init__(self, *, user_id: int, status: "raw.base.UserStatus") -> None:
        self.user_id = user_id  # long
        self.status = status  # UserStatus

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        status = TLObject.read(data)
        
        return UpdateUserStatus(user_id=user_id, status=status)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(self.status.write())
        
        return data.getvalue()
