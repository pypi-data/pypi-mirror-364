from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateUserPhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0xdd87974``

    Parameters:
        user_id: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        photo: :obj:`UserProfilePhoto <pyeitaa.raw.base.UserProfilePhoto>`
        previous: ``bool``
    """

    __slots__: List[str] = ["user_id", "date", "photo", "previous"]

    ID = -0xdd87974
    QUALNAME = "types.UpdateUserPhoto"

    def __init__(self, *, user_id: int, date: int, photo: "raw.base.UserProfilePhoto", previous: bool) -> None:
        self.user_id = user_id  # long
        self.date = date  # int
        self.photo = photo  # UserProfilePhoto
        self.previous = previous  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        date = Int.read(data)
        
        photo = TLObject.read(data)
        
        previous = Bool.read(data)
        
        return UpdateUserPhoto(user_id=user_id, date=date, photo=photo, previous=previous)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Int(self.date))
        
        data.write(self.photo.write())
        
        data.write(Bool(self.previous))
        
        return data.getvalue()
