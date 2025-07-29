from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Photo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.photos.Photo`.

    Details:
        - Layer: ``135``
        - ID: ``0x20212ca8``

    Parameters:
        photo: :obj:`Photo <pyeitaa.raw.base.Photo>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`photos.UpdateProfilePhoto <pyeitaa.raw.functions.photos.UpdateProfilePhoto>`
            - :obj:`photos.UploadProfilePhoto <pyeitaa.raw.functions.photos.UploadProfilePhoto>`
    """

    __slots__: List[str] = ["photo", "users"]

    ID = 0x20212ca8
    QUALNAME = "types.photos.Photo"

    def __init__(self, *, photo: "raw.base.Photo", users: List["raw.base.User"]) -> None:
        self.photo = photo  # Photo
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        photo = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return Photo(photo=photo, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.photo.write())
        
        data.write(Vector(self.users))
        
        return data.getvalue()
