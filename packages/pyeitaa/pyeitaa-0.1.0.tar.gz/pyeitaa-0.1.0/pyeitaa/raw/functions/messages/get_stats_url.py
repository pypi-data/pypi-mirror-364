from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetStatsURL(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7ed3d51a``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        params: ``str``
        dark (optional): ``bool``

    Returns:
        :obj:`StatsURL <pyeitaa.raw.base.StatsURL>`
    """

    __slots__: List[str] = ["peer", "params", "dark"]

    ID = -0x7ed3d51a
    QUALNAME = "functions.messages.GetStatsURL"

    def __init__(self, *, peer: "raw.base.InputPeer", params: str, dark: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.params = params  # string
        self.dark = dark  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        dark = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        params = String.read(data)
        
        return GetStatsURL(peer=peer, params=params, dark=dark)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.dark else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(String(self.params))
        
        return data.getvalue()
