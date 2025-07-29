from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UrlAuthResultAccepted(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.UrlAuthResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7073f1b2``

    Parameters:
        url: ``str``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.RequestUrlAuth <pyeitaa.raw.functions.messages.RequestUrlAuth>`
            - :obj:`messages.AcceptUrlAuth <pyeitaa.raw.functions.messages.AcceptUrlAuth>`
    """

    __slots__: List[str] = ["url"]

    ID = -0x7073f1b2
    QUALNAME = "types.UrlAuthResultAccepted"

    def __init__(self, *, url: str) -> None:
        self.url = url  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        return UrlAuthResultAccepted(url=url)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        return data.getvalue()
