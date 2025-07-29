from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetWebPagePreview(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x74974f34``

    Parameters:
        message: ``str``
        entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`

    Returns:
        :obj:`MessageMedia <pyeitaa.raw.base.MessageMedia>`
    """

    __slots__: List[str] = ["message", "entities"]

    ID = -0x74974f34
    QUALNAME = "functions.messages.GetWebPagePreview"

    def __init__(self, *, message: str, entities: Optional[List["raw.base.MessageEntity"]] = None) -> None:
        self.message = message  # string
        self.entities = entities  # flags.3?Vector<MessageEntity>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        message = String.read(data)
        
        entities = TLObject.read(data) if flags & (1 << 3) else []
        
        return GetWebPagePreview(message=message, entities=entities)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 3) if self.entities is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.message))
        
        if self.entities is not None:
            data.write(Vector(self.entities))
        
        return data.getvalue()
