from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class RecoverPassword(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x37096c70``

    Parameters:
        code: ``str``
        new_settings (optional): :obj:`account.PasswordInputSettings <pyeitaa.raw.base.account.PasswordInputSettings>`

    Returns:
        :obj:`auth.Authorization <pyeitaa.raw.base.auth.Authorization>`
    """

    __slots__: List[str] = ["code", "new_settings"]

    ID = 0x37096c70
    QUALNAME = "functions.auth.RecoverPassword"

    def __init__(self, *, code: str, new_settings: "raw.base.account.PasswordInputSettings" = None) -> None:
        self.code = code  # string
        self.new_settings = new_settings  # flags.0?account.PasswordInputSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        code = String.read(data)
        
        new_settings = TLObject.read(data) if flags & (1 << 0) else None
        
        return RecoverPassword(code=code, new_settings=new_settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.new_settings is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.code))
        
        if self.new_settings is not None:
            data.write(self.new_settings.write())
        
        return data.getvalue()
