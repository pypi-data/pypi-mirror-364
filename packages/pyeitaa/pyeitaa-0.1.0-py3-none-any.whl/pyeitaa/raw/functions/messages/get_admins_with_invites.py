from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetAdminsWithInvites(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3920e6ef``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`

    Returns:
        :obj:`messages.ChatAdminsWithInvites <pyeitaa.raw.base.messages.ChatAdminsWithInvites>`
    """

    __slots__: List[str] = ["peer"]

    ID = 0x3920e6ef
    QUALNAME = "functions.messages.GetAdminsWithInvites"

    def __init__(self, *, peer: "raw.base.InputPeer") -> None:
        self.peer = peer  # InputPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        return GetAdminsWithInvites(peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        return data.getvalue()
