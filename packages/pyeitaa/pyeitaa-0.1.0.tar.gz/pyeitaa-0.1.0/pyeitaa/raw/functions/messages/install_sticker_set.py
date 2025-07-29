from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InstallStickerSet(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x38701ba0``

    Parameters:
        stickerset: :obj:`InputStickerSet <pyeitaa.raw.base.InputStickerSet>`
        archived: ``bool``

    Returns:
        :obj:`messages.StickerSetInstallResult <pyeitaa.raw.base.messages.StickerSetInstallResult>`
    """

    __slots__: List[str] = ["stickerset", "archived"]

    ID = -0x38701ba0
    QUALNAME = "functions.messages.InstallStickerSet"

    def __init__(self, *, stickerset: "raw.base.InputStickerSet", archived: bool) -> None:
        self.stickerset = stickerset  # InputStickerSet
        self.archived = archived  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        stickerset = TLObject.read(data)
        
        archived = Bool.read(data)
        
        return InstallStickerSet(stickerset=stickerset, archived=archived)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.stickerset.write())
        
        data.write(Bool(self.archived))
        
        return data.getvalue()
