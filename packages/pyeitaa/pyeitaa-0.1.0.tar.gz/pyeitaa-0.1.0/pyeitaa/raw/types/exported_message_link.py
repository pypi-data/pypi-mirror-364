from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ExportedMessageLink(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ExportedMessageLink`.

    Details:
        - Layer: ``135``
        - ID: ``0x5dab1af4``

    Parameters:
        link: ``str``
        html: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.ExportMessageLink <pyeitaa.raw.functions.channels.ExportMessageLink>`
    """

    __slots__: List[str] = ["link", "html"]

    ID = 0x5dab1af4
    QUALNAME = "types.ExportedMessageLink"

    def __init__(self, *, link: str, html: str) -> None:
        self.link = link  # string
        self.html = html  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        link = String.read(data)
        
        html = String.read(data)
        
        return ExportedMessageLink(link=link, html=html)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.link))
        
        data.write(String(self.html))
        
        return data.getvalue()
