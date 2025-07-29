from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class AdsInputAdsLocationTrends(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.AdsLocation`.

    Details:
        - Layer: ``135``
        - ID: ``0x5cda5250``

    Parameters:
        groupTitle: ``str``
    """

    __slots__: List[str] = ["groupTitle"]

    ID = 0x5cda5250
    QUALNAME = "types.AdsInputAdsLocationTrends"

    def __init__(self, *, groupTitle: str) -> None:
        self.groupTitle = groupTitle  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        groupTitle = String.read(data)
        
        return AdsInputAdsLocationTrends(groupTitle=groupTitle)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.groupTitle))
        
        return data.getvalue()
