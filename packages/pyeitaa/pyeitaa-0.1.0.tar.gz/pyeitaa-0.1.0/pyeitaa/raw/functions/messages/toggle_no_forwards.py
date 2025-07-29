from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ToggleNoForwards(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4ee1505e``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        enabled: ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "enabled"]

    ID = -0x4ee1505e
    QUALNAME = "functions.messages.ToggleNoForwards"

    def __init__(self, *, peer: "raw.base.InputPeer", enabled: bool) -> None:
        self.peer = peer  # InputPeer
        self.enabled = enabled  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        enabled = Bool.read(data)
        
        return ToggleNoForwards(peer=peer, enabled=enabled)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Bool(self.enabled))
        
        return data.getvalue()
