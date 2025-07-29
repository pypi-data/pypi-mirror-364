from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PasswordKdfAlgo`.

    Details:
        - Layer: ``135``
        - ID: ``0x3a912d4a``

    Parameters:
        salt1: ``bytes``
        salt2: ``bytes``
        g: ``int`` ``32-bit``
        p: ``bytes``
    """

    __slots__: List[str] = ["salt1", "salt2", "g", "p"]

    ID = 0x3a912d4a
    QUALNAME = "types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow"

    def __init__(self, *, salt1: bytes, salt2: bytes, g: int, p: bytes) -> None:
        self.salt1 = salt1  # bytes
        self.salt2 = salt2  # bytes
        self.g = g  # int
        self.p = p  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        salt1 = Bytes.read(data)
        
        salt2 = Bytes.read(data)
        
        g = Int.read(data)
        
        p = Bytes.read(data)
        
        return PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow(salt1=salt1, salt2=salt2, g=g, p=p)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.salt1))
        
        data.write(Bytes(self.salt2))
        
        data.write(Int(self.g))
        
        data.write(Bytes(self.p))
        
        return data.getvalue()
