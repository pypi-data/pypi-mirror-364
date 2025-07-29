from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SecurePasswordKdfAlgoSHA512(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecurePasswordKdfAlgo`.

    Details:
        - Layer: ``135``
        - ID: ``-0x79b8e26e``

    Parameters:
        salt: ``bytes``
    """

    __slots__: List[str] = ["salt"]

    ID = -0x79b8e26e
    QUALNAME = "types.SecurePasswordKdfAlgoSHA512"

    def __init__(self, *, salt: bytes) -> None:
        self.salt = salt  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        salt = Bytes.read(data)
        
        return SecurePasswordKdfAlgoSHA512(salt=salt)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.salt))
        
        return data.getvalue()
