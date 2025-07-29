from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class WebPageNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.WebPage`.

    Details:
        - Layer: ``135``
        - ID: ``0x7311ca11``

    Parameters:
        cached_page_views (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPage <pyeitaa.raw.functions.messages.GetWebPage>`
    """

    __slots__: List[str] = ["cached_page_views"]

    ID = 0x7311ca11
    QUALNAME = "types.WebPageNotModified"

    def __init__(self, *, cached_page_views: Optional[int] = None) -> None:
        self.cached_page_views = cached_page_views  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        cached_page_views = Int.read(data) if flags & (1 << 0) else None
        return WebPageNotModified(cached_page_views=cached_page_views)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.cached_page_views is not None else 0
        data.write(Int(flags))
        
        if self.cached_page_views is not None:
            data.write(Int(self.cached_page_views))
        
        return data.getvalue()
