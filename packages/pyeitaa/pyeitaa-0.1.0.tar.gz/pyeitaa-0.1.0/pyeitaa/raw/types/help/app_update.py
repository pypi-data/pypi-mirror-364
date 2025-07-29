from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class AppUpdate(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.AppUpdate`.

    Details:
        - Layer: ``135``
        - ID: ``-0x334431d0``

    Parameters:
        id: ``int`` ``32-bit``
        version: ``str``
        text: ``str``
        entities: List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
        can_not_skip (optional): ``bool``
        document (optional): :obj:`Document <pyeitaa.raw.base.Document>`
        url (optional): ``str``
        sticker (optional): :obj:`Document <pyeitaa.raw.base.Document>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetAppUpdate <pyeitaa.raw.functions.help.GetAppUpdate>`
    """

    __slots__: List[str] = ["id", "version", "text", "entities", "can_not_skip", "document", "url", "sticker"]

    ID = -0x334431d0
    QUALNAME = "types.help.AppUpdate"

    def __init__(self, *, id: int, version: str, text: str, entities: List["raw.base.MessageEntity"], can_not_skip: Optional[bool] = None, document: "raw.base.Document" = None, url: Optional[str] = None, sticker: "raw.base.Document" = None) -> None:
        self.id = id  # int
        self.version = version  # string
        self.text = text  # string
        self.entities = entities  # Vector<MessageEntity>
        self.can_not_skip = can_not_skip  # flags.0?true
        self.document = document  # flags.1?Document
        self.url = url  # flags.2?string
        self.sticker = sticker  # flags.3?Document

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        can_not_skip = True if flags & (1 << 0) else False
        id = Int.read(data)
        
        version = String.read(data)
        
        text = String.read(data)
        
        entities = TLObject.read(data)
        
        document = TLObject.read(data) if flags & (1 << 1) else None
        
        url = String.read(data) if flags & (1 << 2) else None
        sticker = TLObject.read(data) if flags & (1 << 3) else None
        
        return AppUpdate(id=id, version=version, text=text, entities=entities, can_not_skip=can_not_skip, document=document, url=url, sticker=sticker)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.can_not_skip else 0
        flags |= (1 << 1) if self.document is not None else 0
        flags |= (1 << 2) if self.url is not None else 0
        flags |= (1 << 3) if self.sticker is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.id))
        
        data.write(String(self.version))
        
        data.write(String(self.text))
        
        data.write(Vector(self.entities))
        
        if self.document is not None:
            data.write(self.document.write())
        
        if self.url is not None:
            data.write(String(self.url))
        
        if self.sticker is not None:
            data.write(self.sticker.write())
        
        return data.getvalue()
