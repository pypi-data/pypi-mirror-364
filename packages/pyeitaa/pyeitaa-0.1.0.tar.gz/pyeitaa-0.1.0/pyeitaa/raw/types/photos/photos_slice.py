from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PhotosSlice(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.photos.Photos`.

    Details:
        - Layer: ``135``
        - ID: ``0x15051f54``

    Parameters:
        count: ``int`` ``32-bit``
        photos: List of :obj:`Photo <pyeitaa.raw.base.Photo>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`photos.GetUserPhotos <pyeitaa.raw.functions.photos.GetUserPhotos>`
    """

    __slots__: List[str] = ["count", "photos", "users"]

    ID = 0x15051f54
    QUALNAME = "types.photos.PhotosSlice"

    def __init__(self, *, count: int, photos: List["raw.base.Photo"], users: List["raw.base.User"]) -> None:
        self.count = count  # int
        self.photos = photos  # Vector<Photo>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        photos = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return PhotosSlice(count=count, photos=photos, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        data.write(Vector(self.photos))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
