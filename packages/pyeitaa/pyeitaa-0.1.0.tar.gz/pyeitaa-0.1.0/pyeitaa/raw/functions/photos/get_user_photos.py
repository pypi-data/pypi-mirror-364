from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetUserPhotos(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6e32cd58``

    Parameters:
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        offset: ``int`` ``32-bit``
        max_id: ``int`` ``64-bit``
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`photos.Photos <pyeitaa.raw.base.photos.Photos>`
    """

    __slots__: List[str] = ["user_id", "offset", "max_id", "limit"]

    ID = -0x6e32cd58
    QUALNAME = "functions.photos.GetUserPhotos"

    def __init__(self, *, user_id: "raw.base.InputUser", offset: int, max_id: int, limit: int) -> None:
        self.user_id = user_id  # InputUser
        self.offset = offset  # int
        self.max_id = max_id  # long
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = TLObject.read(data)
        
        offset = Int.read(data)
        
        max_id = Long.read(data)
        
        limit = Int.read(data)
        
        return GetUserPhotos(user_id=user_id, offset=offset, max_id=max_id, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.user_id.write())
        
        data.write(Int(self.offset))
        
        data.write(Long(self.max_id))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
