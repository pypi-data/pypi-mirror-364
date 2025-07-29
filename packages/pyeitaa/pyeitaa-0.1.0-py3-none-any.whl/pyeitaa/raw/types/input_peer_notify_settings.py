from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class InputPeerNotifySettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputPeerNotifySettings`.

    Details:
        - Layer: ``135``
        - ID: ``-0x63c2e672``

    Parameters:
        show_previews (optional): ``bool``
        silent (optional): ``bool``
        mute_until (optional): ``int`` ``32-bit``
        sound (optional): ``str``
    """

    __slots__: List[str] = ["show_previews", "silent", "mute_until", "sound"]

    ID = -0x63c2e672
    QUALNAME = "types.InputPeerNotifySettings"

    def __init__(self, *, show_previews: Optional[bool] = None, silent: Optional[bool] = None, mute_until: Optional[int] = None, sound: Optional[str] = None) -> None:
        self.show_previews = show_previews  # flags.0?Bool
        self.silent = silent  # flags.1?Bool
        self.mute_until = mute_until  # flags.2?int
        self.sound = sound  # flags.3?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        show_previews = Bool.read(data) if flags & (1 << 0) else None
        silent = Bool.read(data) if flags & (1 << 1) else None
        mute_until = Int.read(data) if flags & (1 << 2) else None
        sound = String.read(data) if flags & (1 << 3) else None
        return InputPeerNotifySettings(show_previews=show_previews, silent=silent, mute_until=mute_until, sound=sound)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.show_previews is not None else 0
        flags |= (1 << 1) if self.silent is not None else 0
        flags |= (1 << 2) if self.mute_until is not None else 0
        flags |= (1 << 3) if self.sound is not None else 0
        data.write(Int(flags))
        
        if self.show_previews is not None:
            data.write(Bool(self.show_previews))
        
        if self.silent is not None:
            data.write(Bool(self.silent))
        
        if self.mute_until is not None:
            data.write(Int(self.mute_until))
        
        if self.sound is not None:
            data.write(String(self.sound))
        
        return data.getvalue()
