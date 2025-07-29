from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResetPasswordOk(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.ResetPasswordResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0x16d929c2``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.ResetPassword <pyeitaa.raw.functions.account.ResetPassword>`
    """

    __slots__: List[str] = []

    ID = -0x16d929c2
    QUALNAME = "types.account.ResetPasswordOk"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return ResetPasswordOk()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
