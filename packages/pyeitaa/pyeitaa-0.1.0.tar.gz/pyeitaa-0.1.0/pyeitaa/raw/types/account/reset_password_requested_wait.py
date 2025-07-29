from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResetPasswordRequestedWait(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.ResetPasswordResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0x16100383``

    Parameters:
        until_date: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.ResetPassword <pyeitaa.raw.functions.account.ResetPassword>`
    """

    __slots__: List[str] = ["until_date"]

    ID = -0x16100383
    QUALNAME = "types.account.ResetPasswordRequestedWait"

    def __init__(self, *, until_date: int) -> None:
        self.until_date = until_date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        until_date = Int.read(data)
        
        return ResetPasswordRequestedWait(until_date=until_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.until_date))
        
        return data.getvalue()
