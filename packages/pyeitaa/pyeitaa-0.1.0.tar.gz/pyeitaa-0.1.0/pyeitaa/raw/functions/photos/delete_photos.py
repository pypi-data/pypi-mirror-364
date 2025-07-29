from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DeletePhotos(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x783080d1``

    Parameters:
        id: List of :obj:`InputPhoto <pyeitaa.raw.base.InputPhoto>`

    Returns:
        List of ``int`` ``64-bit``
    """

    __slots__: List[str] = ["id"]

    ID = -0x783080d1
    QUALNAME = "functions.photos.DeletePhotos"

    def __init__(self, *, id: List["raw.base.InputPhoto"]) -> None:
        self.id = id  # Vector<InputPhoto>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return DeletePhotos(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.id))
        
        return data.getvalue()
