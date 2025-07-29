from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SaveDefaultGroupCallJoinAs(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x575e1f8c``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        join_as: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "join_as"]

    ID = 0x575e1f8c
    QUALNAME = "functions.phone.SaveDefaultGroupCallJoinAs"

    def __init__(self, *, peer: "raw.base.InputPeer", join_as: "raw.base.InputPeer") -> None:
        self.peer = peer  # InputPeer
        self.join_as = join_as  # InputPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        join_as = TLObject.read(data)
        
        return SaveDefaultGroupCallJoinAs(peer=peer, join_as=join_as)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.join_as.write())
        
        return data.getvalue()
