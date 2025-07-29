from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetNotifyExceptions(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x53577479``

    Parameters:
        compare_sound (optional): ``bool``
        peer (optional): :obj:`InputNotifyPeer <pyeitaa.raw.base.InputNotifyPeer>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["compare_sound", "peer"]

    ID = 0x53577479
    QUALNAME = "functions.account.GetNotifyExceptions"

    def __init__(self, *, compare_sound: Optional[bool] = None, peer: "raw.base.InputNotifyPeer" = None) -> None:
        self.compare_sound = compare_sound  # flags.1?true
        self.peer = peer  # flags.0?InputNotifyPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        compare_sound = True if flags & (1 << 1) else False
        peer = TLObject.read(data) if flags & (1 << 0) else None
        
        return GetNotifyExceptions(compare_sound=compare_sound, peer=peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.compare_sound else 0
        flags |= (1 << 0) if self.peer is not None else 0
        data.write(Int(flags))
        
        if self.peer is not None:
            data.write(self.peer.write())
        
        return data.getvalue()
