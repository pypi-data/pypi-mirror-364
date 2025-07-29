from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SendEncryptedService(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x32d439a4``

    Parameters:
        peer: :obj:`InputEncryptedChat <pyeitaa.raw.base.InputEncryptedChat>`
        random_id: ``int`` ``64-bit``
        data: ``bytes``

    Returns:
        :obj:`messages.SentEncryptedMessage <pyeitaa.raw.base.messages.SentEncryptedMessage>`
    """

    __slots__: List[str] = ["peer", "random_id", "data"]

    ID = 0x32d439a4
    QUALNAME = "functions.messages.SendEncryptedService"

    def __init__(self, *, peer: "raw.base.InputEncryptedChat", random_id: int, data: bytes) -> None:
        self.peer = peer  # InputEncryptedChat
        self.random_id = random_id  # long
        self.data = data  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        random_id = Long.read(data)
        
        data = Bytes.read(data)
        
        return SendEncryptedService(peer=peer, random_id=random_id, data=data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Long(self.random_id))
        
        data.write(Bytes(self.data))
        
        return data.getvalue()
