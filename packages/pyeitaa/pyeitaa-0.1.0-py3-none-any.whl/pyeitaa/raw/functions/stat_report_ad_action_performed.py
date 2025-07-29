from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class StatReportAdActionPerformed(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4b355559``

    Parameters:
        statAd: :obj:`StatAd <pyeitaa.raw.base.StatAd>`

    Returns:
        :obj:`StatReportAdActionPerformed <pyeitaa.raw.base.StatReportAdActionPerformed>`
    """

    __slots__: List[str] = ["statAd"]

    ID = -0x4b355559
    QUALNAME = "functions.StatReportAdActionPerformed"

    def __init__(self, *, statAd: "raw.base.StatAd") -> None:
        self.statAd = statAd  # StatAd

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        statAd = TLObject.read(data)
        
        return StatReportAdActionPerformed(statAd=statAd)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.statAd.write())
        
        return data.getvalue()
