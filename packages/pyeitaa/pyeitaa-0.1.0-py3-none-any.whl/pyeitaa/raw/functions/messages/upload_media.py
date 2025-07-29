from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UploadMedia(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x519bc2b1``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        media: :obj:`InputMedia <pyeitaa.raw.base.InputMedia>`

    Returns:
        :obj:`MessageMedia <pyeitaa.raw.base.MessageMedia>`
    """

    __slots__: List[str] = ["peer", "media"]

    ID = 0x519bc2b1
    QUALNAME = "functions.messages.UploadMedia"

    def __init__(self, *, peer: "raw.base.InputPeer", media: "raw.base.InputMedia") -> None:
        self.peer = peer  # InputPeer
        self.media = media  # InputMedia

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        media = TLObject.read(data)
        
        return UploadMedia(peer=peer, media=media)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.media.write())
        
        return data.getvalue()
