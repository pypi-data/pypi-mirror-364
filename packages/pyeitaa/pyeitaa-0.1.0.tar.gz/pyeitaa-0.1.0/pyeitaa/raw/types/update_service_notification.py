from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateServiceNotification(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x141b97e7``

    Parameters:
        type: ``str``
        message: ``str``
        media: :obj:`MessageMedia <pyeitaa.raw.base.MessageMedia>`
        entities: List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
        popup (optional): ``bool``
        inbox_date (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["type", "message", "media", "entities", "popup", "inbox_date"]

    ID = -0x141b97e7
    QUALNAME = "types.UpdateServiceNotification"

    def __init__(self, *, type: str, message: str, media: "raw.base.MessageMedia", entities: List["raw.base.MessageEntity"], popup: Optional[bool] = None, inbox_date: Optional[int] = None) -> None:
        self.type = type  # string
        self.message = message  # string
        self.media = media  # MessageMedia
        self.entities = entities  # Vector<MessageEntity>
        self.popup = popup  # flags.0?true
        self.inbox_date = inbox_date  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        popup = True if flags & (1 << 0) else False
        inbox_date = Int.read(data) if flags & (1 << 1) else None
        type = String.read(data)
        
        message = String.read(data)
        
        media = TLObject.read(data)
        
        entities = TLObject.read(data)
        
        return UpdateServiceNotification(type=type, message=message, media=media, entities=entities, popup=popup, inbox_date=inbox_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.popup else 0
        flags |= (1 << 1) if self.inbox_date is not None else 0
        data.write(Int(flags))
        
        if self.inbox_date is not None:
            data.write(Int(self.inbox_date))
        
        data.write(String(self.type))
        
        data.write(String(self.message))
        
        data.write(self.media.write())
        
        data.write(Vector(self.entities))
        
        return data.getvalue()
