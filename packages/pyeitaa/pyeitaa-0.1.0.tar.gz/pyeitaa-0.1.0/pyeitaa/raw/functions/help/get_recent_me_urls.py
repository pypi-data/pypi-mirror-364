from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetRecentMeUrls(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3dc0f114``

    Parameters:
        referer: ``str``

    Returns:
        :obj:`help.RecentMeUrls <pyeitaa.raw.base.help.RecentMeUrls>`
    """

    __slots__: List[str] = ["referer"]

    ID = 0x3dc0f114
    QUALNAME = "functions.help.GetRecentMeUrls"

    def __init__(self, *, referer: str) -> None:
        self.referer = referer  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        referer = String.read(data)
        
        return GetRecentMeUrls(referer=referer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.referer))
        
        return data.getvalue()
