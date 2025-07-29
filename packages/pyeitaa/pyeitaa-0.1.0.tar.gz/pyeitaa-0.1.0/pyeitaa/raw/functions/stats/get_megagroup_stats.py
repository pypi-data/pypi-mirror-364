from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetMegagroupStats(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x232079f9``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        dark (optional): ``bool``

    Returns:
        :obj:`stats.MegagroupStats <pyeitaa.raw.base.stats.MegagroupStats>`
    """

    __slots__: List[str] = ["channel", "dark"]

    ID = -0x232079f9
    QUALNAME = "functions.stats.GetMegagroupStats"

    def __init__(self, *, channel: "raw.base.InputChannel", dark: Optional[bool] = None) -> None:
        self.channel = channel  # InputChannel
        self.dark = dark  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        dark = True if flags & (1 << 0) else False
        channel = TLObject.read(data)
        
        return GetMegagroupStats(channel=channel, dark=dark)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.dark else 0
        data.write(Int(flags))
        
        data.write(self.channel.write())
        
        return data.getvalue()
