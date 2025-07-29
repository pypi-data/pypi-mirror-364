from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputMediaPhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4c45f9cb``

    Parameters:
        id: :obj:`InputPhoto <pyeitaa.raw.base.InputPhoto>`
        ttl_seconds (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "ttl_seconds"]

    ID = -0x4c45f9cb
    QUALNAME = "types.InputMediaPhoto"

    def __init__(self, *, id: "raw.base.InputPhoto", ttl_seconds: Optional[int] = None) -> None:
        self.id = id  # InputPhoto
        self.ttl_seconds = ttl_seconds  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = TLObject.read(data)
        
        ttl_seconds = Int.read(data) if flags & (1 << 0) else None
        return InputMediaPhoto(id=id, ttl_seconds=ttl_seconds)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.ttl_seconds is not None else 0
        data.write(Int(flags))
        
        data.write(self.id.write())
        
        if self.ttl_seconds is not None:
            data.write(Int(self.ttl_seconds))
        
        return data.getvalue()
