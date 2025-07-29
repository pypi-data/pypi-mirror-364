from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputBotInlineResultDocument(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputBotInlineResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7023c``

    Parameters:
        id: ``str``
        type: ``str``
        document: :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        send_message: :obj:`InputBotInlineMessage <pyeitaa.raw.base.InputBotInlineMessage>`
        title (optional): ``str``
        description (optional): ``str``
    """

    __slots__: List[str] = ["id", "type", "document", "send_message", "title", "description"]

    ID = -0x7023c
    QUALNAME = "types.InputBotInlineResultDocument"

    def __init__(self, *, id: str, type: str, document: "raw.base.InputDocument", send_message: "raw.base.InputBotInlineMessage", title: Optional[str] = None, description: Optional[str] = None) -> None:
        self.id = id  # string
        self.type = type  # string
        self.document = document  # InputDocument
        self.send_message = send_message  # InputBotInlineMessage
        self.title = title  # flags.1?string
        self.description = description  # flags.2?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = String.read(data)
        
        type = String.read(data)
        
        title = String.read(data) if flags & (1 << 1) else None
        description = String.read(data) if flags & (1 << 2) else None
        document = TLObject.read(data)
        
        send_message = TLObject.read(data)
        
        return InputBotInlineResultDocument(id=id, type=type, document=document, send_message=send_message, title=title, description=description)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.title is not None else 0
        flags |= (1 << 2) if self.description is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.id))
        
        data.write(String(self.type))
        
        if self.title is not None:
            data.write(String(self.title))
        
        if self.description is not None:
            data.write(String(self.description))
        
        data.write(self.document.write())
        
        data.write(self.send_message.write())
        
        return data.getvalue()
