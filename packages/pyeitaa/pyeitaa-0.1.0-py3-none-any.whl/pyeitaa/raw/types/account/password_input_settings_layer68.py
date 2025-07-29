from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class PasswordInputSettingsLayer68(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.PasswordInputSettings`.

    Details:
        - Layer: ``135``
        - ID: ``0x21ffa60d``

    Parameters:
        new_salt (optional): ``bytes``
        new_password_hash (optional): ``bytes``
        hint (optional): ``str``
        email (optional): ``str``
        new_secure_salt (optional): ``bytes``
        new_secure_secret (optional): ``bytes``
        new_secure_secret_id (optional): ``int`` ``64-bit``
    """

    __slots__: List[str] = ["new_salt", "new_password_hash", "hint", "email", "new_secure_salt", "new_secure_secret", "new_secure_secret_id"]

    ID = 0x21ffa60d
    QUALNAME = "types.account.PasswordInputSettingsLayer68"

    def __init__(self, *, new_salt: Optional[bytes] = None, new_password_hash: Optional[bytes] = None, hint: Optional[str] = None, email: Optional[str] = None, new_secure_salt: Optional[bytes] = None, new_secure_secret: Optional[bytes] = None, new_secure_secret_id: Optional[int] = None) -> None:
        self.new_salt = new_salt  # flags.0?bytes
        self.new_password_hash = new_password_hash  # flags.0?bytes
        self.hint = hint  # flags.0?string
        self.email = email  # flags.1?string
        self.new_secure_salt = new_secure_salt  # flags.2?bytes
        self.new_secure_secret = new_secure_secret  # flags.2?bytes
        self.new_secure_secret_id = new_secure_secret_id  # flags.2?long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        new_salt = Bytes.read(data) if flags & (1 << 0) else None
        new_password_hash = Bytes.read(data) if flags & (1 << 0) else None
        hint = String.read(data) if flags & (1 << 0) else None
        email = String.read(data) if flags & (1 << 1) else None
        new_secure_salt = Bytes.read(data) if flags & (1 << 2) else None
        new_secure_secret = Bytes.read(data) if flags & (1 << 2) else None
        new_secure_secret_id = Long.read(data) if flags & (1 << 2) else None
        return PasswordInputSettingsLayer68(new_salt=new_salt, new_password_hash=new_password_hash, hint=hint, email=email, new_secure_salt=new_secure_salt, new_secure_secret=new_secure_secret, new_secure_secret_id=new_secure_secret_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.new_salt is not None else 0
        flags |= (1 << 0) if self.new_password_hash is not None else 0
        flags |= (1 << 0) if self.hint is not None else 0
        flags |= (1 << 1) if self.email is not None else 0
        flags |= (1 << 2) if self.new_secure_salt is not None else 0
        flags |= (1 << 2) if self.new_secure_secret is not None else 0
        flags |= (1 << 2) if self.new_secure_secret_id is not None else 0
        data.write(Int(flags))
        
        if self.new_salt is not None:
            data.write(Bytes(self.new_salt))
        
        if self.new_password_hash is not None:
            data.write(Bytes(self.new_password_hash))
        
        if self.hint is not None:
            data.write(String(self.hint))
        
        if self.email is not None:
            data.write(String(self.email))
        
        if self.new_secure_salt is not None:
            data.write(Bytes(self.new_secure_salt))
        
        if self.new_secure_secret is not None:
            data.write(Bytes(self.new_secure_secret))
        
        if self.new_secure_secret_id is not None:
            data.write(Long(self.new_secure_secret_id))
        
        return data.getvalue()
