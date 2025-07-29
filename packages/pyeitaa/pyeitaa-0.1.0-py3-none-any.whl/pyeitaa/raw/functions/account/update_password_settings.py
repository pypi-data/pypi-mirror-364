from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdatePasswordSettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5a64efd1``

    Parameters:
        password: :obj:`InputCheckPasswordSRP <pyeitaa.raw.base.InputCheckPasswordSRP>`
        new_settings: :obj:`account.PasswordInputSettings <pyeitaa.raw.base.account.PasswordInputSettings>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["password", "new_settings"]

    ID = -0x5a64efd1
    QUALNAME = "functions.account.UpdatePasswordSettings"

    def __init__(self, *, password: "raw.base.InputCheckPasswordSRP", new_settings: "raw.base.account.PasswordInputSettings") -> None:
        self.password = password  # InputCheckPasswordSRP
        self.new_settings = new_settings  # account.PasswordInputSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        password = TLObject.read(data)
        
        new_settings = TLObject.read(data)
        
        return UpdatePasswordSettings(password=password, new_settings=new_settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.password.write())
        
        data.write(self.new_settings.write())
        
        return data.getvalue()
