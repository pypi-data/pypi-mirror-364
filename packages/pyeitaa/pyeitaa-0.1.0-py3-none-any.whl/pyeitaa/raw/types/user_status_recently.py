from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UserStatusRecently(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.UserStatus`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1d90bd0f``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x1d90bd0f
    QUALNAME = "types.UserStatusRecently"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return UserStatusRecently()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
