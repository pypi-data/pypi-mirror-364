from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SecureCredentialsEncrypted(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureCredentialsEncrypted`.

    Details:
        - Layer: ``135``
        - ID: ``0x33f0ea47``

    Parameters:
        data: ``bytes``
        hash: ``bytes``
        secret: ``bytes``
    """

    __slots__: List[str] = ["data", "hash", "secret"]

    ID = 0x33f0ea47
    QUALNAME = "types.SecureCredentialsEncrypted"

    def __init__(self, *, data: bytes, hash: bytes, secret: bytes) -> None:
        self.data = data  # bytes
        self.hash = hash  # bytes
        self.secret = secret  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        data = Bytes.read(data)
        
        hash = Bytes.read(data)
        
        secret = Bytes.read(data)
        
        return SecureCredentialsEncrypted(data=data, hash=hash, secret=secret)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.data))
        
        data.write(Bytes(self.hash))
        
        data.write(Bytes(self.secret))
        
        return data.getvalue()
