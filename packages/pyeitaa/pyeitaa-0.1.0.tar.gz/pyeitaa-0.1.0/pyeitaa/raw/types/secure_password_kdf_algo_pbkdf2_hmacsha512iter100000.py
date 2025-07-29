from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecurePasswordKdfAlgo`.

    Details:
        - Layer: ``135``
        - ID: ``-0x440d2260``

    Parameters:
        salt: ``bytes``
    """

    __slots__: List[str] = ["salt"]

    ID = -0x440d2260
    QUALNAME = "types.SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000"

    def __init__(self, *, salt: bytes) -> None:
        self.salt = salt  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        salt = Bytes.read(data)
        
        return SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000(salt=salt)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.salt))
        
        return data.getvalue()
