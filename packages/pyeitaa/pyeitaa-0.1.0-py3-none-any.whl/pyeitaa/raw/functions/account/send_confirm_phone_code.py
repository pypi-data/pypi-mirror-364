from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SendConfirmPhoneCode(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1b3faa88``

    Parameters:
        hash: ``str``
        settings: :obj:`CodeSettings <pyeitaa.raw.base.CodeSettings>`

    Returns:
        :obj:`auth.SentCode <pyeitaa.raw.base.auth.SentCode>`
    """

    __slots__: List[str] = ["hash", "settings"]

    ID = 0x1b3faa88
    QUALNAME = "functions.account.SendConfirmPhoneCode"

    def __init__(self, *, hash: str, settings: "raw.base.CodeSettings") -> None:
        self.hash = hash  # string
        self.settings = settings  # CodeSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = String.read(data)
        
        settings = TLObject.read(data)
        
        return SendConfirmPhoneCode(hash=hash, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.hash))
        
        data.write(self.settings.write())
        
        return data.getvalue()
