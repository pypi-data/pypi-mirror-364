from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateProfilePhoto(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x72d4742c``

    Parameters:
        id: :obj:`InputPhoto <pyeitaa.raw.base.InputPhoto>`

    Returns:
        :obj:`photos.Photo <pyeitaa.raw.base.photos.Photo>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x72d4742c
    QUALNAME = "functions.photos.UpdateProfilePhoto"

    def __init__(self, *, id: "raw.base.InputPhoto") -> None:
        self.id = id  # InputPhoto

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return UpdateProfilePhoto(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        return data.getvalue()
