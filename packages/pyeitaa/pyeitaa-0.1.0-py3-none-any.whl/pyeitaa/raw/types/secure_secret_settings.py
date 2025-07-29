from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SecureSecretSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureSecretSettings`.

    Details:
        - Layer: ``135``
        - ID: ``0x1527bcac``

    Parameters:
        secure_algo: :obj:`SecurePasswordKdfAlgo <pyeitaa.raw.base.SecurePasswordKdfAlgo>`
        secure_secret: ``bytes``
        secure_secret_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["secure_algo", "secure_secret", "secure_secret_id"]

    ID = 0x1527bcac
    QUALNAME = "types.SecureSecretSettings"

    def __init__(self, *, secure_algo: "raw.base.SecurePasswordKdfAlgo", secure_secret: bytes, secure_secret_id: int) -> None:
        self.secure_algo = secure_algo  # SecurePasswordKdfAlgo
        self.secure_secret = secure_secret  # bytes
        self.secure_secret_id = secure_secret_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        secure_algo = TLObject.read(data)
        
        secure_secret = Bytes.read(data)
        
        secure_secret_id = Long.read(data)
        
        return SecureSecretSettings(secure_algo=secure_algo, secure_secret=secure_secret, secure_secret_id=secure_secret_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.secure_algo.write())
        
        data.write(Bytes(self.secure_secret))
        
        data.write(Long(self.secure_secret_id))
        
        return data.getvalue()
