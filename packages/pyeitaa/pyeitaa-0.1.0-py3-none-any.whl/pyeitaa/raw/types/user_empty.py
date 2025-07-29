from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UserEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.User`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2c43b486``

    Parameters:
        id: ``int`` ``64-bit``

    See Also:
        This object can be returned by 4 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.UpdateProfile <pyeitaa.raw.functions.account.UpdateProfile>`
            - :obj:`account.UpdateUsername <pyeitaa.raw.functions.account.UpdateUsername>`
            - :obj:`account.ChangePhone <pyeitaa.raw.functions.account.ChangePhone>`
            - :obj:`users.GetUsers <pyeitaa.raw.functions.users.GetUsers>`
    """

    __slots__: List[str] = ["id"]

    ID = -0x2c43b486
    QUALNAME = "types.UserEmpty"

    def __init__(self, *, id: int) -> None:
        self.id = id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        return UserEmpty(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        return data.getvalue()
