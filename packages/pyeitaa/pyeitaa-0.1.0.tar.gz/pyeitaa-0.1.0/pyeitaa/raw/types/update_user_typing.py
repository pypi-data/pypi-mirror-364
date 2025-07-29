from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateUserTyping(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3fe17a81``

    Parameters:
        user_id: ``int`` ``64-bit``
        action: :obj:`SendMessageAction <pyeitaa.raw.base.SendMessageAction>`
    """

    __slots__: List[str] = ["user_id", "action"]

    ID = -0x3fe17a81
    QUALNAME = "types.UpdateUserTyping"

    def __init__(self, *, user_id: int, action: "raw.base.SendMessageAction") -> None:
        self.user_id = user_id  # long
        self.action = action  # SendMessageAction

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        action = TLObject.read(data)
        
        return UpdateUserTyping(user_id=user_id, action=action)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(self.action.write())
        
        return data.getvalue()
