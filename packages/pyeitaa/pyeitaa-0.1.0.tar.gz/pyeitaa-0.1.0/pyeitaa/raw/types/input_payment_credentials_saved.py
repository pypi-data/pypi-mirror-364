from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputPaymentCredentialsSaved(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputPaymentCredentials`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3ef14d31``

    Parameters:
        id: ``str``
        tmp_password: ``bytes``
    """

    __slots__: List[str] = ["id", "tmp_password"]

    ID = -0x3ef14d31
    QUALNAME = "types.InputPaymentCredentialsSaved"

    def __init__(self, *, id: str, tmp_password: bytes) -> None:
        self.id = id  # string
        self.tmp_password = tmp_password  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = String.read(data)
        
        tmp_password = Bytes.read(data)
        
        return InputPaymentCredentialsSaved(id=id, tmp_password=tmp_password)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.id))
        
        data.write(Bytes(self.tmp_password))
        
        return data.getvalue()
