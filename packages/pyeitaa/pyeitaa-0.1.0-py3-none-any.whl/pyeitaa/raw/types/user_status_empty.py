from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UserStatusEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.UserStatus`.

    Details:
        - Layer: ``135``
        - ID: ``0x9d05049``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = 0x9d05049
    QUALNAME = "types.UserStatusEmpty"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return UserStatusEmpty()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
