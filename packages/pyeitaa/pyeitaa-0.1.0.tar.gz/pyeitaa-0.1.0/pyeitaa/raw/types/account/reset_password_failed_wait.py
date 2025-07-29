from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResetPasswordFailedWait(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.ResetPasswordResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1c88679f``

    Parameters:
        retry_date: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.ResetPassword <pyeitaa.raw.functions.account.ResetPassword>`
    """

    __slots__: List[str] = ["retry_date"]

    ID = -0x1c88679f
    QUALNAME = "types.account.ResetPasswordFailedWait"

    def __init__(self, *, retry_date: int) -> None:
        self.retry_date = retry_date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        retry_date = Int.read(data)
        
        return ResetPasswordFailedWait(retry_date=retry_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.retry_date))
        
        return data.getvalue()
