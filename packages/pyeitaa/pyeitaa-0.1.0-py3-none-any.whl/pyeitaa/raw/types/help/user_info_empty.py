from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UserInfoEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.UserInfo`.

    Details:
        - Layer: ``135``
        - ID: ``-0xc51d113``

    **No parameters required.**

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`help.GetUserInfo <pyeitaa.raw.functions.help.GetUserInfo>`
            - :obj:`help.EditUserInfo <pyeitaa.raw.functions.help.EditUserInfo>`
    """

    __slots__: List[str] = []

    ID = -0xc51d113
    QUALNAME = "types.help.UserInfoEmpty"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return UserInfoEmpty()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
