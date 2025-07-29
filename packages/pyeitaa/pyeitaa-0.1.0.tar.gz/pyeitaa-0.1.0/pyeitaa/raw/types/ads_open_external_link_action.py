from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class AdsOpenExternalLinkAction(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.AdsClickAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x630b7275``

    Parameters:
        link: ``str``
    """

    __slots__: List[str] = ["link"]

    ID = -0x630b7275
    QUALNAME = "types.AdsOpenExternalLinkAction"

    def __init__(self, *, link: str) -> None:
        self.link = link  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        link = String.read(data)
        
        return AdsOpenExternalLinkAction(link=link)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.link))
        
        return data.getvalue()
