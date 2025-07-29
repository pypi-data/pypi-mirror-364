from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateGroupCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x14b24500``

    Parameters:
        chat_id: ``int`` ``64-bit``
        call: :obj:`GroupCall <pyeitaa.raw.base.GroupCall>`
    """

    __slots__: List[str] = ["chat_id", "call"]

    ID = 0x14b24500
    QUALNAME = "types.UpdateGroupCall"

    def __init__(self, *, chat_id: int, call: "raw.base.GroupCall") -> None:
        self.chat_id = chat_id  # long
        self.call = call  # GroupCall

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        call = TLObject.read(data)
        
        return UpdateGroupCall(chat_id=chat_id, call=call)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        data.write(self.call.write())
        
        return data.getvalue()
