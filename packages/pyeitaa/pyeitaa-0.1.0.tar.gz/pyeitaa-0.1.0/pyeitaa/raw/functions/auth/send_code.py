from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SendCode(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5988dbb1``

    Parameters:
        phone_number: ``str``
        api_id: ``int`` ``32-bit``
        api_hash: ``str``
        settings: :obj:`CodeSettings <pyeitaa.raw.base.CodeSettings>`

    Returns:
        :obj:`auth.SentCode <pyeitaa.raw.base.auth.SentCode>`
    """

    __slots__: List[str] = ["phone_number", "api_id", "api_hash", "settings"]

    ID = -0x5988dbb1
    QUALNAME = "functions.auth.SendCode"

    def __init__(self, *, phone_number: str, api_id: int, api_hash: str, settings: "raw.base.CodeSettings") -> None:
        self.phone_number = phone_number  # string
        self.api_id = api_id  # int
        self.api_hash = api_hash  # string
        self.settings = settings  # CodeSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_number = String.read(data)
        
        api_id = Int.read(data)
        
        api_hash = String.read(data)
        
        settings = TLObject.read(data)
        
        return SendCode(phone_number=phone_number, api_id=api_id, api_hash=api_hash, settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone_number))
        
        data.write(Int(self.api_id))
        
        data.write(String(self.api_hash))
        
        data.write(self.settings.write())
        
        return data.getvalue()
