from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class PasswordSettings68(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.PasswordSettings`.

    Details:
        - Layer: ``135``
        - ID: ``0x7bd9c3f1``

    Parameters:
        email (optional): ``str``
        secure_salt (optional): ``str``
        secure_secret (optional): ``str``
        secure_secret_id (optional): ``str``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetPasswordSettings <pyeitaa.raw.functions.account.GetPasswordSettings>`
            - :obj:`account.GetPasswordSettings68 <pyeitaa.raw.functions.account.GetPasswordSettings68>`
    """

    __slots__: List[str] = ["email", "secure_salt", "secure_secret", "secure_secret_id"]

    ID = 0x7bd9c3f1
    QUALNAME = "types.account.PasswordSettings68"

    def __init__(self, *, email: Optional[str] = None, secure_salt: Optional[str] = None, secure_secret: Optional[str] = None, secure_secret_id: Optional[str] = None) -> None:
        self.email = email  # flags.0?string
        self.secure_salt = secure_salt  # flags.1?string
        self.secure_secret = secure_secret  # flags.2?string
        self.secure_secret_id = secure_secret_id  # flags.3?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        email = String.read(data) if flags & (1 << 0) else None
        secure_salt = String.read(data) if flags & (1 << 1) else None
        secure_secret = String.read(data) if flags & (1 << 2) else None
        secure_secret_id = String.read(data) if flags & (1 << 3) else None
        return PasswordSettings68(email=email, secure_salt=secure_salt, secure_secret=secure_secret, secure_secret_id=secure_secret_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.email is not None else 0
        flags |= (1 << 1) if self.secure_salt is not None else 0
        flags |= (1 << 2) if self.secure_secret is not None else 0
        flags |= (1 << 3) if self.secure_secret_id is not None else 0
        data.write(Int(flags))
        
        if self.email is not None:
            data.write(String(self.email))
        
        if self.secure_salt is not None:
            data.write(String(self.secure_salt))
        
        if self.secure_secret is not None:
            data.write(String(self.secure_secret))
        
        if self.secure_secret_id is not None:
            data.write(String(self.secure_secret_id))
        
        return data.getvalue()
