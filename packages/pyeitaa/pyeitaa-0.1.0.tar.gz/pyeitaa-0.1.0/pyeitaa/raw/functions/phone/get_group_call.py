from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetGroupCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x41845db``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`phone.GroupCall <pyeitaa.raw.base.phone.GroupCall>`
    """

    __slots__: List[str] = ["call", "limit"]

    ID = 0x41845db
    QUALNAME = "functions.phone.GetGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall", limit: int) -> None:
        self.call = call  # InputGroupCall
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        limit = Int.read(data)
        
        return GetGroupCall(call=call, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(Int(self.limit))
        
        return data.getvalue()
