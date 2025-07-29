from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockAudio(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7fbc9e16``

    Parameters:
        audio_id: ``int`` ``64-bit``
        caption: :obj:`PageCaption <pyeitaa.raw.base.PageCaption>`
    """

    __slots__: List[str] = ["audio_id", "caption"]

    ID = -0x7fbc9e16
    QUALNAME = "types.PageBlockAudio"

    def __init__(self, *, audio_id: int, caption: "raw.base.PageCaption") -> None:
        self.audio_id = audio_id  # long
        self.caption = caption  # PageCaption

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        audio_id = Long.read(data)
        
        caption = TLObject.read(data)
        
        return PageBlockAudio(audio_id=audio_id, caption=caption)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.audio_id))
        
        data.write(self.caption.write())
        
        return data.getvalue()
