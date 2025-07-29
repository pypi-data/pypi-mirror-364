from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ExportGroupCallInvite(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x19559b81``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        can_self_unmute (optional): ``bool``

    Returns:
        :obj:`phone.ExportedGroupCallInvite <pyeitaa.raw.base.phone.ExportedGroupCallInvite>`
    """

    __slots__: List[str] = ["call", "can_self_unmute"]

    ID = -0x19559b81
    QUALNAME = "functions.phone.ExportGroupCallInvite"

    def __init__(self, *, call: "raw.base.InputGroupCall", can_self_unmute: Optional[bool] = None) -> None:
        self.call = call  # InputGroupCall
        self.can_self_unmute = can_self_unmute  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        can_self_unmute = True if flags & (1 << 0) else False
        call = TLObject.read(data)
        
        return ExportGroupCallInvite(call=call, can_self_unmute=can_self_unmute)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.can_self_unmute else 0
        data.write(Int(flags))
        
        data.write(self.call.write())
        
        return data.getvalue()
