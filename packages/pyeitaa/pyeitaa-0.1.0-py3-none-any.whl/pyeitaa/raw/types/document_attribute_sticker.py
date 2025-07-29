from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class DocumentAttributeSticker(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DocumentAttribute`.

    Details:
        - Layer: ``135``
        - ID: ``0x6319d612``

    Parameters:
        alt: ``str``
        stickerset: :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`
        mask (optional): ``bool``
        mask_coords (optional): :obj:`MaskCoords <pyeitaa.raw.base.MaskCoords>`
    """

    __slots__: List[str] = ["alt", "stickerset", "mask", "mask_coords"]

    ID = 0x6319d612
    QUALNAME = "types.DocumentAttributeSticker"

    def __init__(self, *, alt: str, stickerset: "raw.base.InputStickerSet", mask: Optional[bool] = None, mask_coords: "raw.base.MaskCoords" = None) -> None:
        self.alt = alt  # string
        self.stickerset = stickerset  # InputStickerSet
        self.mask = mask  # flags.1?true
        self.mask_coords = mask_coords  # flags.0?MaskCoords

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        mask = True if flags & (1 << 1) else False
        alt = String.read(data)
        
        stickerset = TLObject.read(data)
        
        mask_coords = TLObject.read(data) if flags & (1 << 0) else None
        
        return DocumentAttributeSticker(alt=alt, stickerset=stickerset, mask=mask, mask_coords=mask_coords)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.mask else 0
        flags |= (1 << 0) if self.mask_coords is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.alt))
        
        data.write(self.stickerset.write())
        
        if self.mask_coords is not None:
            data.write(self.mask_coords.write())
        
        return data.getvalue()
