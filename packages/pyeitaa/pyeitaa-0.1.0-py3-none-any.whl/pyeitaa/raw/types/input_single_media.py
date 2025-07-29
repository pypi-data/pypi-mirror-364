from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputSingleMedia(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputSingleMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x1cc6e91f``

    Parameters:
        media: :obj:`InputMedia <pyeitaa.raw.base.InputMedia>`
        random_id: ``int`` ``64-bit``
        message: ``str``
        entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
    """

    __slots__: List[str] = ["media", "random_id", "message", "entities"]

    ID = 0x1cc6e91f
    QUALNAME = "types.InputSingleMedia"

    def __init__(self, *, media: "raw.base.InputMedia", random_id: int, message: str, entities: Optional[List["raw.base.MessageEntity"]] = None) -> None:
        self.media = media  # InputMedia
        self.random_id = random_id  # long
        self.message = message  # string
        self.entities = entities  # flags.0?Vector<MessageEntity>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        media = TLObject.read(data)
        
        random_id = Long.read(data)
        
        message = String.read(data)
        
        entities = TLObject.read(data) if flags & (1 << 0) else []
        
        return InputSingleMedia(media=media, random_id=random_id, message=message, entities=entities)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.entities is not None else 0
        data.write(Int(flags))
        
        data.write(self.media.write())
        
        data.write(Long(self.random_id))
        
        data.write(String(self.message))
        
        if self.entities is not None:
            data.write(Vector(self.entities))
        
        return data.getvalue()
