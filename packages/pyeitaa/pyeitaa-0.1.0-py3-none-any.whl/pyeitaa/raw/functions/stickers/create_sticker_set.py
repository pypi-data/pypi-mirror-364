from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class CreateStickerSet(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6fde5499``

    Parameters:
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        title: ``str``
        short_name: ``str``
        stickers: List of :obj:`InputStickerSetItem <pyeitaa.raw.base.InputStickerSetItem>`
        masks (optional): ``bool``
        animated (optional): ``bool``
        thumb (optional): :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        software (optional): ``str``

    Returns:
        :obj:`messages.StickerSet <pyeitaa.raw.base.messages.StickerSet>`
    """

    __slots__: List[str] = ["user_id", "title", "short_name", "stickers", "masks", "animated", "thumb", "software"]

    ID = -0x6fde5499
    QUALNAME = "functions.stickers.CreateStickerSet"

    def __init__(self, *, user_id: "raw.base.InputUser", title: str, short_name: str, stickers: List["raw.base.InputStickerSetItem"], masks: Optional[bool] = None, animated: Optional[bool] = None, thumb: "raw.base.InputDocument" = None, software: Optional[str] = None) -> None:
        self.user_id = user_id  # InputUser
        self.title = title  # string
        self.short_name = short_name  # string
        self.stickers = stickers  # Vector<InputStickerSetItem>
        self.masks = masks  # flags.0?true
        self.animated = animated  # flags.1?true
        self.thumb = thumb  # flags.2?InputDocument
        self.software = software  # flags.3?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        masks = True if flags & (1 << 0) else False
        animated = True if flags & (1 << 1) else False
        user_id = TLObject.read(data)
        
        title = String.read(data)
        
        short_name = String.read(data)
        
        thumb = TLObject.read(data) if flags & (1 << 2) else None
        
        stickers = TLObject.read(data)
        
        software = String.read(data) if flags & (1 << 3) else None
        return CreateStickerSet(user_id=user_id, title=title, short_name=short_name, stickers=stickers, masks=masks, animated=animated, thumb=thumb, software=software)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.masks else 0
        flags |= (1 << 1) if self.animated else 0
        flags |= (1 << 2) if self.thumb is not None else 0
        flags |= (1 << 3) if self.software is not None else 0
        data.write(Int(flags))
        
        data.write(self.user_id.write())
        
        data.write(String(self.title))
        
        data.write(String(self.short_name))
        
        if self.thumb is not None:
            data.write(self.thumb.write())
        
        data.write(Vector(self.stickers))
        
        if self.software is not None:
            data.write(String(self.software))
        
        return data.getvalue()
