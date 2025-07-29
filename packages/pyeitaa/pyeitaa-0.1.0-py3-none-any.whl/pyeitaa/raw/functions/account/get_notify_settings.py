from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetNotifySettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x12b3ad31``

    Parameters:
        peer: :obj:`InputNotifyPeer <pyeitaa.raw.base.InputNotifyPeer>`

    Returns:
        :obj:`PeerNotifySettings <pyeitaa.raw.base.PeerNotifySettings>`
    """

    __slots__: List[str] = ["peer"]

    ID = 0x12b3ad31
    QUALNAME = "functions.account.GetNotifySettings"

    def __init__(self, *, peer: "raw.base.InputNotifyPeer") -> None:
        self.peer = peer  # InputNotifyPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        return GetNotifySettings(peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        return data.getvalue()
