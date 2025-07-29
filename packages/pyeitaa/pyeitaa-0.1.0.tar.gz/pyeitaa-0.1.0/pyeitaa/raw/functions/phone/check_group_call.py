from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class CheckGroupCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4a630689``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        sources: List of ``int`` ``32-bit``

    Returns:
        List of ``int`` ``32-bit``
    """

    __slots__: List[str] = ["call", "sources"]

    ID = -0x4a630689
    QUALNAME = "functions.phone.CheckGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall", sources: List[int]) -> None:
        self.call = call  # InputGroupCall
        self.sources = sources  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        sources = TLObject.read(data, Int)
        
        return CheckGroupCall(call=call, sources=sources)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(Vector(self.sources, Int))
        
        return data.getvalue()
