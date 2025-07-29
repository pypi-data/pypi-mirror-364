from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetAccountTTL(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2442485e``

    Parameters:
        ttl: :obj:`AccountDaysTTL <pyeitaa.raw.base.AccountDaysTTL>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["ttl"]

    ID = 0x2442485e
    QUALNAME = "functions.account.SetAccountTTL"

    def __init__(self, *, ttl: "raw.base.AccountDaysTTL") -> None:
        self.ttl = ttl  # AccountDaysTTL

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        ttl = TLObject.read(data)
        
        return SetAccountTTL(ttl=ttl)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.ttl.write())
        
        return data.getvalue()
