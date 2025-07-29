from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UserStatusOnline(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.UserStatus`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1246c6b7``

    Parameters:
        expires: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["expires"]

    ID = -0x1246c6b7
    QUALNAME = "types.UserStatusOnline"

    def __init__(self, *, expires: int) -> None:
        self.expires = expires  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        expires = Int.read(data)
        
        return UserStatusOnline(expires=expires)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.expires))
        
        return data.getvalue()
