from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SecureData(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureData`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7515413d``

    Parameters:
        data: ``bytes``
        data_hash: ``bytes``
        secret: ``bytes``
    """

    __slots__: List[str] = ["data", "data_hash", "secret"]

    ID = -0x7515413d
    QUALNAME = "types.SecureData"

    def __init__(self, *, data: bytes, data_hash: bytes, secret: bytes) -> None:
        self.data = data  # bytes
        self.data_hash = data_hash  # bytes
        self.secret = secret  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        data = Bytes.read(data)
        
        data_hash = Bytes.read(data)
        
        secret = Bytes.read(data)
        
        return SecureData(data=data, data_hash=data_hash, secret=secret)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.data))
        
        data.write(Bytes(self.data_hash))
        
        data.write(Bytes(self.secret))
        
        return data.getvalue()
