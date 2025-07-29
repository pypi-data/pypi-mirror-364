from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SendEncrypted(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x44fa7a15``

    Parameters:
        peer: :obj:`InputEncryptedChat <pyeitaa.raw.base.InputEncryptedChat>`
        random_id: ``int`` ``64-bit``
        data: ``bytes``
        silent (optional): ``bool``

    Returns:
        :obj:`messages.SentEncryptedMessage <pyeitaa.raw.base.messages.SentEncryptedMessage>`
    """

    __slots__: List[str] = ["peer", "random_id", "data", "silent"]

    ID = 0x44fa7a15
    QUALNAME = "functions.messages.SendEncrypted"

    def __init__(self, *, peer: "raw.base.InputEncryptedChat", random_id: int, data: bytes, silent: Optional[bool] = None) -> None:
        self.peer = peer  # InputEncryptedChat
        self.random_id = random_id  # long
        self.data = data  # bytes
        self.silent = silent  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        silent = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        random_id = Long.read(data)
        
        data = Bytes.read(data)
        
        return SendEncrypted(peer=peer, random_id=random_id, data=data, silent=silent)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.silent else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Long(self.random_id))
        
        data.write(Bytes(self.data))
        
        return data.getvalue()
