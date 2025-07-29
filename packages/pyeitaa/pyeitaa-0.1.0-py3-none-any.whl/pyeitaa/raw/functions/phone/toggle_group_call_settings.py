from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ToggleGroupCallSettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x74bbb43d``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        reset_invite_hash (optional): ``bool``
        join_muted (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "reset_invite_hash", "join_muted"]

    ID = 0x74bbb43d
    QUALNAME = "functions.phone.ToggleGroupCallSettings"

    def __init__(self, *, call: "raw.base.InputGroupCall", reset_invite_hash: Optional[bool] = None, join_muted: Optional[bool] = None) -> None:
        self.call = call  # InputGroupCall
        self.reset_invite_hash = reset_invite_hash  # flags.1?true
        self.join_muted = join_muted  # flags.0?Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        reset_invite_hash = True if flags & (1 << 1) else False
        call = TLObject.read(data)
        
        join_muted = Bool.read(data) if flags & (1 << 0) else None
        return ToggleGroupCallSettings(call=call, reset_invite_hash=reset_invite_hash, join_muted=join_muted)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.reset_invite_hash else 0
        flags |= (1 << 0) if self.join_muted is not None else 0
        data.write(Int(flags))
        
        data.write(self.call.write())
        
        if self.join_muted is not None:
            data.write(Bool(self.join_muted))
        
        return data.getvalue()
