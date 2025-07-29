from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputPrivacyValueDisallowUsers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputPrivacyRule`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6feefb99``

    Parameters:
        users: List of :obj:`InputUser <pyeitaa.raw.base.InputUser>`
    """

    __slots__: List[str] = ["users"]

    ID = -0x6feefb99
    QUALNAME = "types.InputPrivacyValueDisallowUsers"

    def __init__(self, *, users: List["raw.base.InputUser"]) -> None:
        self.users = users  # Vector<InputUser>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        users = TLObject.read(data)
        
        return InputPrivacyValueDisallowUsers(users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.users))
        
        return data.getvalue()
