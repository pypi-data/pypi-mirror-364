from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UploadEncryptedFile(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x5057c497``

    Parameters:
        peer: :obj:`InputEncryptedChat <pyeitaa.raw.base.InputEncryptedChat>`
        file: :obj:`InputEncryptedFile <pyeitaa.raw.base.InputEncryptedFile>`

    Returns:
        :obj:`EncryptedFile <pyeitaa.raw.base.EncryptedFile>`
    """

    __slots__: List[str] = ["peer", "file"]

    ID = 0x5057c497
    QUALNAME = "functions.messages.UploadEncryptedFile"

    def __init__(self, *, peer: "raw.base.InputEncryptedChat", file: "raw.base.InputEncryptedFile") -> None:
        self.peer = peer  # InputEncryptedChat
        self.file = file  # InputEncryptedFile

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        file = TLObject.read(data)
        
        return UploadEncryptedFile(peer=peer, file=file)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.file.write())
        
        return data.getvalue()
