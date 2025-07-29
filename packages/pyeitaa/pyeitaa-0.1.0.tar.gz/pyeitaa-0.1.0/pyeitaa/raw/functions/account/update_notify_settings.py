from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateNotifySettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7b41a46d``

    Parameters:
        peer: :obj:`InputNotifyPeer <pyeitaa.raw.base.InputNotifyPeer>`
        settings: :obj:`InputPeerNotifySettings <pyeitaa.raw.base.InputPeerNotifySettings>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "settings"]

    ID = -0x7b41a46d
    QUALNAME = "functions.account.UpdateNotifySettings"

    def __init__(self, *, peer: "raw.base.InputNotifyPeer", settings: "raw.base.InputPeerNotifySettings") -> None:
        self.peer = peer  # InputNotifyPeer
        self.settings = settings  # InputPeerNotifySettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        settings = TLObject.read(data)
        
        return UpdateNotifySettings(peer=peer, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.settings.write())
        
        return data.getvalue()
