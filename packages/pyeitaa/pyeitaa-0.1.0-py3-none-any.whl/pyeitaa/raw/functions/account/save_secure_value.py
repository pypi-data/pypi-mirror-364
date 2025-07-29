from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SaveSecureValue(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x76601ce3``

    Parameters:
        value: :obj:`InputSecureValue <pyeitaa.raw.base.InputSecureValue>`
        secure_secret_id: ``int`` ``64-bit``

    Returns:
        :obj:`SecureValue <pyeitaa.raw.base.SecureValue>`
    """

    __slots__: List[str] = ["value", "secure_secret_id"]

    ID = -0x76601ce3
    QUALNAME = "functions.account.SaveSecureValue"

    def __init__(self, *, value: "raw.base.InputSecureValue", secure_secret_id: int) -> None:
        self.value = value  # InputSecureValue
        self.secure_secret_id = secure_secret_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        value = TLObject.read(data)
        
        secure_secret_id = Long.read(data)
        
        return SaveSecureValue(value=value, secure_secret_id=secure_secret_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.value.write())
        
        data.write(Long(self.secure_secret_id))
        
        return data.getvalue()
