from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PasswordInputSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.PasswordInputSettings`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3dc8d837``

    Parameters:
        new_algo (optional): :obj:`PasswordKdfAlgo <pyeitaa.raw.base.PasswordKdfAlgo>`
        new_password_hash (optional): ``bytes``
        hint (optional): ``str``
        email (optional): ``str``
        new_secure_settings (optional): :obj:`SecureSecretSettings <pyeitaa.raw.base.SecureSecretSettings>`
    """

    __slots__: List[str] = ["new_algo", "new_password_hash", "hint", "email", "new_secure_settings"]

    ID = -0x3dc8d837
    QUALNAME = "types.account.PasswordInputSettings"

    def __init__(self, *, new_algo: "raw.base.PasswordKdfAlgo" = None, new_password_hash: Optional[bytes] = None, hint: Optional[str] = None, email: Optional[str] = None, new_secure_settings: "raw.base.SecureSecretSettings" = None) -> None:
        self.new_algo = new_algo  # flags.0?PasswordKdfAlgo
        self.new_password_hash = new_password_hash  # flags.0?bytes
        self.hint = hint  # flags.0?string
        self.email = email  # flags.1?string
        self.new_secure_settings = new_secure_settings  # flags.2?SecureSecretSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        new_algo = TLObject.read(data) if flags & (1 << 0) else None
        
        new_password_hash = Bytes.read(data) if flags & (1 << 0) else None
        hint = String.read(data) if flags & (1 << 0) else None
        email = String.read(data) if flags & (1 << 1) else None
        new_secure_settings = TLObject.read(data) if flags & (1 << 2) else None
        
        return PasswordInputSettings(new_algo=new_algo, new_password_hash=new_password_hash, hint=hint, email=email, new_secure_settings=new_secure_settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.new_algo is not None else 0
        flags |= (1 << 0) if self.new_password_hash is not None else 0
        flags |= (1 << 0) if self.hint is not None else 0
        flags |= (1 << 1) if self.email is not None else 0
        flags |= (1 << 2) if self.new_secure_settings is not None else 0
        data.write(Int(flags))
        
        if self.new_algo is not None:
            data.write(self.new_algo.write())
        
        if self.new_password_hash is not None:
            data.write(Bytes(self.new_password_hash))
        
        if self.hint is not None:
            data.write(String(self.hint))
        
        if self.email is not None:
            data.write(String(self.email))
        
        if self.new_secure_settings is not None:
            data.write(self.new_secure_settings.write())
        
        return data.getvalue()
