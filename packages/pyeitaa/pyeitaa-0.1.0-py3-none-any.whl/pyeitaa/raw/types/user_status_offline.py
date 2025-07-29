from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UserStatusOffline(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.UserStatus`.

    Details:
        - Layer: ``135``
        - ID: ``0x8c703f``

    Parameters:
        was_online: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["was_online"]

    ID = 0x8c703f
    QUALNAME = "types.UserStatusOffline"

    def __init__(self, *, was_online: int) -> None:
        self.was_online = was_online  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        was_online = Int.read(data)
        
        return UserStatusOffline(was_online=was_online)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.was_online))
        
        return data.getvalue()
