from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Photos(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.photos.Photos`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7235955b``

    Parameters:
        photos: List of :obj:`Photo <pyeitaa.raw.base.Photo>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`photos.GetUserPhotos <pyeitaa.raw.functions.photos.GetUserPhotos>`
    """

    __slots__: List[str] = ["photos", "users"]

    ID = -0x7235955b
    QUALNAME = "types.photos.Photos"

    def __init__(self, *, photos: List["raw.base.Photo"], users: List["raw.base.User"]) -> None:
        self.photos = photos  # Vector<Photo>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        photos = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return Photos(photos=photos, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.photos))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
