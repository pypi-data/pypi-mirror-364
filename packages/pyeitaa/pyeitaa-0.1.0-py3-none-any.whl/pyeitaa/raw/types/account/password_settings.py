from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PasswordSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.PasswordSettings`.

    Details:
        - Layer: ``135``
        - ID: ``-0x65a3cc1b``

    Parameters:
        email (optional): ``str``
        secure_settings (optional): :obj:`SecureSecretSettings <pyeitaa.raw.base.SecureSecretSettings>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetPasswordSettings <pyeitaa.raw.functions.account.GetPasswordSettings>`
            - :obj:`account.GetPasswordSettings68 <pyeitaa.raw.functions.account.GetPasswordSettings68>`
    """

    __slots__: List[str] = ["email", "secure_settings"]

    ID = -0x65a3cc1b
    QUALNAME = "types.account.PasswordSettings"

    def __init__(self, *, email: Optional[str] = None, secure_settings: "raw.base.SecureSecretSettings" = None) -> None:
        self.email = email  # flags.0?string
        self.secure_settings = secure_settings  # flags.1?SecureSecretSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        email = String.read(data) if flags & (1 << 0) else None
        secure_settings = TLObject.read(data) if flags & (1 << 1) else None
        
        return PasswordSettings(email=email, secure_settings=secure_settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.email is not None else 0
        flags |= (1 << 1) if self.secure_settings is not None else 0
        data.write(Int(flags))
        
        if self.email is not None:
            data.write(String(self.email))
        
        if self.secure_settings is not None:
            data.write(self.secure_settings.write())
        
        return data.getvalue()
