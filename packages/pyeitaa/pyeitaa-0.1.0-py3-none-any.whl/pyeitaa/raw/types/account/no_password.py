from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class NoPassword(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.Password`.

    Details:
        - Layer: ``135``
        - ID: ``0x5ea182f6``

    Parameters:
        new_salt: ``bytes``
        new_secure_salt: ``bytes``
        secure_random: ``bytes``
        email_unconfirmed_pattern: ``str``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetPassword <pyeitaa.raw.functions.account.GetPassword>`
            - :obj:`account.GetPasswordLayer68 <pyeitaa.raw.functions.account.GetPasswordLayer68>`
    """

    __slots__: List[str] = ["new_salt", "new_secure_salt", "secure_random", "email_unconfirmed_pattern"]

    ID = 0x5ea182f6
    QUALNAME = "types.account.NoPassword"

    def __init__(self, *, new_salt: bytes, new_secure_salt: bytes, secure_random: bytes, email_unconfirmed_pattern: str) -> None:
        self.new_salt = new_salt  # bytes
        self.new_secure_salt = new_secure_salt  # bytes
        self.secure_random = secure_random  # bytes
        self.email_unconfirmed_pattern = email_unconfirmed_pattern  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        new_salt = Bytes.read(data)
        
        new_secure_salt = Bytes.read(data)
        
        secure_random = Bytes.read(data)
        
        email_unconfirmed_pattern = String.read(data)
        
        return NoPassword(new_salt=new_salt, new_secure_salt=new_secure_salt, secure_random=secure_random, email_unconfirmed_pattern=email_unconfirmed_pattern)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.new_salt))
        
        data.write(Bytes(self.new_secure_salt))
        
        data.write(Bytes(self.secure_random))
        
        data.write(String(self.email_unconfirmed_pattern))
        
        return data.getvalue()
