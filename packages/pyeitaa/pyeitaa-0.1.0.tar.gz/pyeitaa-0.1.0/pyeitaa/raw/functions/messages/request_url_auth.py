from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class RequestUrlAuth(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x198fb446``

    Parameters:
        peer (optional): :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        msg_id (optional): ``int`` ``32-bit``
        button_id (optional): ``int`` ``32-bit``
        url (optional): ``str``

    Returns:
        :obj:`UrlAuthResult <pyeitaa.raw.base.UrlAuthResult>`
    """

    __slots__: List[str] = ["peer", "msg_id", "button_id", "url"]

    ID = 0x198fb446
    QUALNAME = "functions.messages.RequestUrlAuth"

    def __init__(self, *, peer: "raw.base.InputPeer" = None, msg_id: Optional[int] = None, button_id: Optional[int] = None, url: Optional[str] = None) -> None:
        self.peer = peer  # flags.1?InputPeer
        self.msg_id = msg_id  # flags.1?int
        self.button_id = button_id  # flags.1?int
        self.url = url  # flags.2?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        peer = TLObject.read(data) if flags & (1 << 1) else None
        
        msg_id = Int.read(data) if flags & (1 << 1) else None
        button_id = Int.read(data) if flags & (1 << 1) else None
        url = String.read(data) if flags & (1 << 2) else None
        return RequestUrlAuth(peer=peer, msg_id=msg_id, button_id=button_id, url=url)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.peer is not None else 0
        flags |= (1 << 1) if self.msg_id is not None else 0
        flags |= (1 << 1) if self.button_id is not None else 0
        flags |= (1 << 2) if self.url is not None else 0
        data.write(Int(flags))
        
        if self.peer is not None:
            data.write(self.peer.write())
        
        if self.msg_id is not None:
            data.write(Int(self.msg_id))
        
        if self.button_id is not None:
            data.write(Int(self.button_id))
        
        if self.url is not None:
            data.write(String(self.url))
        
        return data.getvalue()
