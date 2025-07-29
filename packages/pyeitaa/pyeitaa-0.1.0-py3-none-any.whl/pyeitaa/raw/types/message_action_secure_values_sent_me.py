from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageActionSecureValuesSentMe(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x1b287353``

    Parameters:
        values: List of :obj:`SecureValue <pyeitaa.raw.base.SecureValue>`
        credentials: :obj:`SecureCredentialsEncrypted <pyeitaa.raw.base.SecureCredentialsEncrypted>`
    """

    __slots__: List[str] = ["values", "credentials"]

    ID = 0x1b287353
    QUALNAME = "types.MessageActionSecureValuesSentMe"

    def __init__(self, *, values: List["raw.base.SecureValue"], credentials: "raw.base.SecureCredentialsEncrypted") -> None:
        self.values = values  # Vector<SecureValue>
        self.credentials = credentials  # SecureCredentialsEncrypted

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        values = TLObject.read(data)
        
        credentials = TLObject.read(data)
        
        return MessageActionSecureValuesSentMe(values=values, credentials=credentials)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.values))
        
        data.write(self.credentials.write())
        
        return data.getvalue()
