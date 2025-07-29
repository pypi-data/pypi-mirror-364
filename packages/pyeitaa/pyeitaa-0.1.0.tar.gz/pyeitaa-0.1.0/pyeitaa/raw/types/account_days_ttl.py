from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class AccountDaysTTL(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.AccountDaysTTL`.

    Details:
        - Layer: ``135``
        - ID: ``-0x472f5021``

    Parameters:
        days: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAccountTTL <pyeitaa.raw.functions.account.GetAccountTTL>`
    """

    __slots__: List[str] = ["days"]

    ID = -0x472f5021
    QUALNAME = "types.AccountDaysTTL"

    def __init__(self, *, days: int) -> None:
        self.days = days  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        days = Int.read(data)
        
        return AccountDaysTTL(days=days)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.days))
        
        return data.getvalue()
