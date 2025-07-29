from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Double
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputAppEvent(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputAppEvent`.

    Details:
        - Layer: ``135``
        - ID: ``0x1d1b1245``

    Parameters:
        time: ``float`` ``64-bit``
        type: ``str``
        peer: ``int`` ``64-bit``
        data: :obj:`JSONValue <pyeitaa.raw.base.JSONValue>`
    """

    __slots__: List[str] = ["time", "type", "peer", "data"]

    ID = 0x1d1b1245
    QUALNAME = "types.InputAppEvent"

    def __init__(self, *, time: float, type: str, peer: int, data: "raw.base.JSONValue") -> None:
        self.time = time  # double
        self.type = type  # string
        self.peer = peer  # long
        self.data = data  # JSONValue

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        time = Double.read(data)
        
        type = String.read(data)
        
        peer = Long.read(data)
        
        data = TLObject.read(data)
        
        return InputAppEvent(time=time, type=type, peer=peer, data=data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Double(self.time))
        
        data.write(String(self.type))
        
        data.write(Long(self.peer))
        
        data.write(self.data.write())
        
        return data.getvalue()
