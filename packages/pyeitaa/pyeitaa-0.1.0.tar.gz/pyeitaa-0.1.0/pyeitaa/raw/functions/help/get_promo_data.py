from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetPromoData(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3f688bdf``

    **No parameters required.**

    Returns:
        :obj:`help.PromoData <pyeitaa.raw.base.help.PromoData>`
    """

    __slots__: List[str] = []

    ID = -0x3f688bdf
    QUALNAME = "functions.help.GetPromoData"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetPromoData()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
