from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateDeviceLocked(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x38df3532``

    Parameters:
        period: ``int`` ``32-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["period"]

    ID = 0x38df3532
    QUALNAME = "functions.account.UpdateDeviceLocked"

    def __init__(self, *, period: int) -> None:
        self.period = period  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        period = Int.read(data)
        
        return UpdateDeviceLocked(period=period)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.period))
        
        return data.getvalue()
