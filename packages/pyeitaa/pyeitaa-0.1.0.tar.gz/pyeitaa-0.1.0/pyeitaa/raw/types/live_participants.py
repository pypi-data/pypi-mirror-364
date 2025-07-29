from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class LiveParticipants(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LiveParticipants`.

    Details:
        - Layer: ``135``
        - ID: ``-0xd167c00``

    Parameters:
        users: List of :obj:`User <pyeitaa.raw.base.User>`
    """

    __slots__: List[str] = ["users"]

    ID = -0xd167c00
    QUALNAME = "types.LiveParticipants"

    def __init__(self, *, users: List["raw.base.User"]) -> None:
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        users = TLObject.read(data)
        
        return LiveParticipants(users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.users))
        
        return data.getvalue()
