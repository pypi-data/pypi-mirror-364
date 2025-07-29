from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class Password2(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.Password2`.

    Details:
        - Layer: ``135``
        - ID: ``-0x35c64bb9``

    Parameters:
        current_salt: ``bytes``
        new_salt: ``bytes``
        new_secure_salt: ``bytes``
        secure_random: ``bytes``
        hint: ``str``
        email_unconfirmed_pattern: ``str``
        has_recovery (optional): ``bool``
        has_secure_values (optional): ``bool``
    """

    __slots__: List[str] = ["current_salt", "new_salt", "new_secure_salt", "secure_random", "hint", "email_unconfirmed_pattern", "has_recovery", "has_secure_values"]

    ID = -0x35c64bb9
    QUALNAME = "types.account.Password2"

    def __init__(self, *, current_salt: bytes, new_salt: bytes, new_secure_salt: bytes, secure_random: bytes, hint: str, email_unconfirmed_pattern: str, has_recovery: Optional[bool] = None, has_secure_values: Optional[bool] = None) -> None:
        self.current_salt = current_salt  # bytes
        self.new_salt = new_salt  # bytes
        self.new_secure_salt = new_secure_salt  # bytes
        self.secure_random = secure_random  # bytes
        self.hint = hint  # string
        self.email_unconfirmed_pattern = email_unconfirmed_pattern  # string
        self.has_recovery = has_recovery  # flags.0?true
        self.has_secure_values = has_secure_values  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        has_recovery = True if flags & (1 << 0) else False
        has_secure_values = True if flags & (1 << 1) else False
        current_salt = Bytes.read(data)
        
        new_salt = Bytes.read(data)
        
        new_secure_salt = Bytes.read(data)
        
        secure_random = Bytes.read(data)
        
        hint = String.read(data)
        
        email_unconfirmed_pattern = String.read(data)
        
        return Password2(current_salt=current_salt, new_salt=new_salt, new_secure_salt=new_secure_salt, secure_random=secure_random, hint=hint, email_unconfirmed_pattern=email_unconfirmed_pattern, has_recovery=has_recovery, has_secure_values=has_secure_values)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.has_recovery else 0
        flags |= (1 << 1) if self.has_secure_values else 0
        data.write(Int(flags))
        
        data.write(Bytes(self.current_salt))
        
        data.write(Bytes(self.new_salt))
        
        data.write(Bytes(self.new_secure_salt))
        
        data.write(Bytes(self.secure_random))
        
        data.write(String(self.hint))
        
        data.write(String(self.email_unconfirmed_pattern))
        
        return data.getvalue()
