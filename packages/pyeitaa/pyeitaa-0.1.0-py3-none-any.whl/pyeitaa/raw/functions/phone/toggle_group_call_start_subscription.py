from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ToggleGroupCallStartSubscription(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x219c34e6``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        subscribed: ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "subscribed"]

    ID = 0x219c34e6
    QUALNAME = "functions.phone.ToggleGroupCallStartSubscription"

    def __init__(self, *, call: "raw.base.InputGroupCall", subscribed: bool) -> None:
        self.call = call  # InputGroupCall
        self.subscribed = subscribed  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        call = TLObject.read(data)
        
        subscribed = Bool.read(data)
        
        return ToggleGroupCallStartSubscription(call=call, subscribed=subscribed)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.call.write())
        
        data.write(Bool(self.subscribed))
        
        return data.getvalue()
