from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateNotifySettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x413d9711``

    Parameters:
        peer: :obj:`NotifyPeer <pyeitaa.raw.base.NotifyPeer>`
        notify_settings: :obj:`PeerNotifySettings <pyeitaa.raw.base.PeerNotifySettings>`
    """

    __slots__: List[str] = ["peer", "notify_settings"]

    ID = -0x413d9711
    QUALNAME = "types.UpdateNotifySettings"

    def __init__(self, *, peer: "raw.base.NotifyPeer", notify_settings: "raw.base.PeerNotifySettings") -> None:
        self.peer = peer  # NotifyPeer
        self.notify_settings = notify_settings  # PeerNotifySettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        notify_settings = TLObject.read(data)
        
        return UpdateNotifySettings(peer=peer, notify_settings=notify_settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.notify_settings.write())
        
        return data.getvalue()
