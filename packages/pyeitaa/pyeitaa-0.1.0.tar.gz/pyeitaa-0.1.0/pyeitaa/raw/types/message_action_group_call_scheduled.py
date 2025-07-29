from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageActionGroupCallScheduled(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4c5f899f``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        schedule_date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["call", "schedule_date"]

    ID = -0x4c5f899f
    QUALNAME = "types.MessageActionGroupCallScheduled"

    def __init__(self, *, call: "raw.base.InputGroupCall", schedule_date: int) -> None:
        self.call = call  # InputGroupCall
        self.schedule_date = schedule_date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        schedule_date = Int.read(data)
        
        return MessageActionGroupCallScheduled(call=call, schedule_date=schedule_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(Int(self.schedule_date))
        
        return data.getvalue()
