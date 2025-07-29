from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UploadImportedMedia(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2a862092``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        import_id: ``int`` ``64-bit``
        file_name: ``str``
        media: :obj:`InputMedia <pyeitaa.raw.base.InputMedia>`

    Returns:
        :obj:`MessageMedia <pyeitaa.raw.base.MessageMedia>`
    """

    __slots__: List[str] = ["peer", "import_id", "file_name", "media"]

    ID = 0x2a862092
    QUALNAME = "functions.messages.UploadImportedMedia"

    def __init__(self, *, peer: "raw.base.InputPeer", import_id: int, file_name: str, media: "raw.base.InputMedia") -> None:
        self.peer = peer  # InputPeer
        self.import_id = import_id  # long
        self.file_name = file_name  # string
        self.media = media  # InputMedia

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        import_id = Long.read(data)
        
        file_name = String.read(data)
        
        media = TLObject.read(data)
        
        return UploadImportedMedia(peer=peer, import_id=import_id, file_name=file_name, media=media)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Long(self.import_id))
        
        data.write(String(self.file_name))
        
        data.write(self.media.write())
        
        return data.getvalue()
