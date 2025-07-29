from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetAttachedStickers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x33a49834``

    Parameters:
        media: :obj:`InputStickeredMedia <pyeitaa.raw.base.InputStickeredMedia>`

    Returns:
        List of :obj:`StickerSetCovered <pyeitaa.raw.base.StickerSetCovered>`
    """

    __slots__: List[str] = ["media"]

    ID = -0x33a49834
    QUALNAME = "functions.messages.GetAttachedStickers"

    def __init__(self, *, media: "raw.base.InputStickeredMedia") -> None:
        self.media = media  # InputStickeredMedia

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        media = TLObject.read(data)
        
        return GetAttachedStickers(media=media)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.media.write())
        
        return data.getvalue()
