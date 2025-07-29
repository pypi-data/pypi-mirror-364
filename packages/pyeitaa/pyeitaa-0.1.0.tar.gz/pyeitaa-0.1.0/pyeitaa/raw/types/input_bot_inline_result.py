from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputBotInlineResult(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputBotInlineResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0x77406ce7``

    Parameters:
        id: ``str``
        type: ``str``
        send_message: :obj:`InputBotInlineMessage <pyeitaa.raw.base.InputBotInlineMessage>`
        title (optional): ``str``
        description (optional): ``str``
        url (optional): ``str``
        thumb (optional): :obj:`InputWebDocument <pyeitaa.raw.base.InputWebDocument>`
        content (optional): :obj:`InputWebDocument <pyeitaa.raw.base.InputWebDocument>`
    """

    __slots__: List[str] = ["id", "type", "send_message", "title", "description", "url", "thumb", "content"]

    ID = -0x77406ce7
    QUALNAME = "types.InputBotInlineResult"

    def __init__(self, *, id: str, type: str, send_message: "raw.base.InputBotInlineMessage", title: Optional[str] = None, description: Optional[str] = None, url: Optional[str] = None, thumb: "raw.base.InputWebDocument" = None, content: "raw.base.InputWebDocument" = None) -> None:
        self.id = id  # string
        self.type = type  # string
        self.send_message = send_message  # InputBotInlineMessage
        self.title = title  # flags.1?string
        self.description = description  # flags.2?string
        self.url = url  # flags.3?string
        self.thumb = thumb  # flags.4?InputWebDocument
        self.content = content  # flags.5?InputWebDocument

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = String.read(data)
        
        type = String.read(data)
        
        title = String.read(data) if flags & (1 << 1) else None
        description = String.read(data) if flags & (1 << 2) else None
        url = String.read(data) if flags & (1 << 3) else None
        thumb = TLObject.read(data) if flags & (1 << 4) else None
        
        content = TLObject.read(data) if flags & (1 << 5) else None
        
        send_message = TLObject.read(data)
        
        return InputBotInlineResult(id=id, type=type, send_message=send_message, title=title, description=description, url=url, thumb=thumb, content=content)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.title is not None else 0
        flags |= (1 << 2) if self.description is not None else 0
        flags |= (1 << 3) if self.url is not None else 0
        flags |= (1 << 4) if self.thumb is not None else 0
        flags |= (1 << 5) if self.content is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.id))
        
        data.write(String(self.type))
        
        if self.title is not None:
            data.write(String(self.title))
        
        if self.description is not None:
            data.write(String(self.description))
        
        if self.url is not None:
            data.write(String(self.url))
        
        if self.thumb is not None:
            data.write(self.thumb.write())
        
        if self.content is not None:
            data.write(self.content.write())
        
        data.write(self.send_message.write())
        
        return data.getvalue()
