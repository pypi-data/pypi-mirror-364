from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class StatsGraph(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StatsGraph`.

    Details:
        - Layer: ``135``
        - ID: ``-0x715b9b4a``

    Parameters:
        json: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
        zoom_token (optional): ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.LoadAsyncGraph <pyeitaa.raw.functions.stats.LoadAsyncGraph>`
    """

    __slots__: List[str] = ["json", "zoom_token"]

    ID = -0x715b9b4a
    QUALNAME = "types.StatsGraph"

    def __init__(self, *, json: "raw.base.DataJSON", zoom_token: Optional[str] = None) -> None:
        self.json = json  # DataJSON
        self.zoom_token = zoom_token  # flags.0?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        json = TLObject.read(data)
        
        zoom_token = String.read(data) if flags & (1 << 0) else None
        return StatsGraph(json=json, zoom_token=zoom_token)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.zoom_token is not None else 0
        data.write(Int(flags))
        
        data.write(self.json.write())
        
        if self.zoom_token is not None:
            data.write(String(self.zoom_token))
        
        return data.getvalue()
