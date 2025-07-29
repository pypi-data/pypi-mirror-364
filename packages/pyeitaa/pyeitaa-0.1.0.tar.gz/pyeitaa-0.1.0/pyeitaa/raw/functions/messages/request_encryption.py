from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class RequestEncryption(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x9b250bd``

    Parameters:
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        random_id: ``int`` ``32-bit``
        g_a: ``bytes``

    Returns:
        :obj:`EncryptedChat <pyeitaa.raw.base.EncryptedChat>`
    """

    __slots__: List[str] = ["user_id", "random_id", "g_a"]

    ID = -0x9b250bd
    QUALNAME = "functions.messages.RequestEncryption"

    def __init__(self, *, user_id: "raw.base.InputUser", random_id: int, g_a: bytes) -> None:
        self.user_id = user_id  # InputUser
        self.random_id = random_id  # int
        self.g_a = g_a  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = TLObject.read(data)
        
        random_id = Int.read(data)
        
        g_a = Bytes.read(data)
        
        return RequestEncryption(user_id=user_id, random_id=random_id, g_a=g_a)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.user_id.write())
        
        data.write(Int(self.random_id))
        
        data.write(Bytes(self.g_a))
        
        return data.getvalue()
