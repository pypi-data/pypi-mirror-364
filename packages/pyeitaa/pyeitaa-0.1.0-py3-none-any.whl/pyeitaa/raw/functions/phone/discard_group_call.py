from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DiscardGroupCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7a777135``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["call"]

    ID = 0x7a777135
    QUALNAME = "functions.phone.DiscardGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall") -> None:
        self.call = call  # InputGroupCall

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        return DiscardGroupCall(call=call)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        return data.getvalue()
