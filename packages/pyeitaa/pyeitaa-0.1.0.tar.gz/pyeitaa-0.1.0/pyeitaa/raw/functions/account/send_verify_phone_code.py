from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SendVerifyPhoneCode(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5a5ca907``

    Parameters:
        phone_number: ``str``
        settings: :obj:`CodeSettings <pyeitaa.raw.base.CodeSettings>`

    Returns:
        :obj:`auth.SentCode <pyeitaa.raw.base.auth.SentCode>`
    """

    __slots__: List[str] = ["phone_number", "settings"]

    ID = -0x5a5ca907
    QUALNAME = "functions.account.SendVerifyPhoneCode"

    def __init__(self, *, phone_number: str, settings: "raw.base.CodeSettings") -> None:
        self.phone_number = phone_number  # string
        self.settings = settings  # CodeSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_number = String.read(data)
        
        settings = TLObject.read(data)
        
        return SendVerifyPhoneCode(phone_number=phone_number, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone_number))
        
        data.write(self.settings.write())
        
        return data.getvalue()
