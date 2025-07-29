from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetTmpPassword(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x449e0b51``

    Parameters:
        password: :obj:`InputCheckPasswordSRP <pyeitaa.raw.base.InputCheckPasswordSRP>`
        period: ``int`` ``32-bit``

    Returns:
        :obj:`account.TmpPassword <pyeitaa.raw.base.account.TmpPassword>`
    """

    __slots__: List[str] = ["password", "period"]

    ID = 0x449e0b51
    QUALNAME = "functions.account.GetTmpPassword"

    def __init__(self, *, password: "raw.base.InputCheckPasswordSRP", period: int) -> None:
        self.password = password  # InputCheckPasswordSRP
        self.period = period  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        password = TLObject.read(data)
        
        period = Int.read(data)
        
        return GetTmpPassword(password=password, period=period)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.password.write())
        
        data.write(Int(self.period))
        
        return data.getvalue()
