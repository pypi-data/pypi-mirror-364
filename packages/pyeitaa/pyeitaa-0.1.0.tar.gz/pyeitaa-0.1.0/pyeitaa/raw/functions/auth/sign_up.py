from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SignUp(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7f111bd9``

    Parameters:
        phone_number: ``str``
        phone_code_hash: ``str``
        phone_code: ``str``
        first_name: ``str``
        last_name: ``str``
        app_info: :obj:`EitaaAppInfo <pyeitaa.raw.base.EitaaAppInfo>`

    Returns:
        :obj:`auth.Authorization <pyeitaa.raw.base.auth.Authorization>`
    """

    __slots__: List[str] = ["phone_number", "phone_code_hash", "phone_code", "first_name", "last_name", "app_info"]

    ID = -0x7f111bd9
    QUALNAME = "functions.auth.SignUp"

    def __init__(self, *, phone_number: str, phone_code_hash: str, phone_code: str, first_name: str, last_name: str, app_info: "raw.base.EitaaAppInfo") -> None:
        self.phone_number = phone_number  # string
        self.phone_code_hash = phone_code_hash  # string
        self.phone_code = phone_code  # string
        self.first_name = first_name  # string
        self.last_name = last_name  # string
        self.app_info = app_info  # EitaaAppInfo

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_number = String.read(data)
        
        phone_code_hash = String.read(data)
        
        phone_code = String.read(data)
        
        first_name = String.read(data)
        
        last_name = String.read(data)
        
        app_info = TLObject.read(data)
        
        return SignUp(phone_number=phone_number, phone_code_hash=phone_code_hash, phone_code=phone_code, first_name=first_name, last_name=last_name, app_info=app_info)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone_number))
        
        data.write(String(self.phone_code_hash))
        
        data.write(String(self.phone_code))
        
        data.write(String(self.first_name))
        
        data.write(String(self.last_name))
        
        data.write(self.app_info.write())
        
        return data.getvalue()
