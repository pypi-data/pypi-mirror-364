from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetAccountTTL(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x8fc711d``

    **No parameters required.**

    Returns:
        :obj:`AccountDaysTTL <pyeitaa.raw.base.AccountDaysTTL>`
    """

    __slots__: List[str] = []

    ID = 0x8fc711d
    QUALNAME = "functions.account.GetAccountTTL"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetAccountTTL()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
