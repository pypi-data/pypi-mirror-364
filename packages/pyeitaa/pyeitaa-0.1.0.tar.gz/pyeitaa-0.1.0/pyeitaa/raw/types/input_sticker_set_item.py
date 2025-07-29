from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputStickerSetItem(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputStickerSetItem`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5f5b6a``

    Parameters:
        document: :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        emoji: ``str``
        mask_coords (optional): :obj:`MaskCoords <pyeitaa.raw.base.MaskCoords>`
    """

    __slots__: List[str] = ["document", "emoji", "mask_coords"]

    ID = -0x5f5b6a
    QUALNAME = "types.InputStickerSetItem"

    def __init__(self, *, document: "raw.base.InputDocument", emoji: str, mask_coords: "raw.base.MaskCoords" = None) -> None:
        self.document = document  # InputDocument
        self.emoji = emoji  # string
        self.mask_coords = mask_coords  # flags.0?MaskCoords

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        document = TLObject.read(data)
        
        emoji = String.read(data)
        
        mask_coords = TLObject.read(data) if flags & (1 << 0) else None
        
        return InputStickerSetItem(document=document, emoji=emoji, mask_coords=mask_coords)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.mask_coords is not None else 0
        data.write(Int(flags))
        
        data.write(self.document.write())
        
        data.write(String(self.emoji))
        
        if self.mask_coords is not None:
            data.write(self.mask_coords.write())
        
        return data.getvalue()
