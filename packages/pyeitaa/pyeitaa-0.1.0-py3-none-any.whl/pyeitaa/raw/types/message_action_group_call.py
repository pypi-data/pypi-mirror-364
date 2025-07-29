from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageActionGroupCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x7a0d7f42``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        duration (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["call", "duration"]

    ID = 0x7a0d7f42
    QUALNAME = "types.MessageActionGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall", duration: Optional[int] = None) -> None:
        self.call = call  # InputGroupCall
        self.duration = duration  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        call = TLObject.read(data)
        
        duration = Int.read(data) if flags & (1 << 0) else None
        return MessageActionGroupCall(call=call, duration=duration)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.duration is not None else 0
        data.write(Int(flags))
        
        data.write(self.call.write())
        
        if self.duration is not None:
            data.write(Int(self.duration))
        
        return data.getvalue()
