from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Password(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.Password`.

    Details:
        - Layer: ``135``
        - ID: ``0x185b184f``

    Parameters:
        new_algo: :obj:`PasswordKdfAlgo <pyeitaa.raw.base.PasswordKdfAlgo>`
        new_secure_algo: :obj:`SecurePasswordKdfAlgo <pyeitaa.raw.base.SecurePasswordKdfAlgo>`
        secure_random: ``bytes``
        has_recovery (optional): ``bool``
        has_secure_values (optional): ``bool``
        has_password (optional): ``bool``
        current_algo (optional): :obj:`PasswordKdfAlgo <pyeitaa.raw.base.PasswordKdfAlgo>`
        srp_B (optional): ``bytes``
        srp_id (optional): ``int`` ``64-bit``
        hint (optional): ``str``
        email_unconfirmed_pattern (optional): ``str``
        pending_reset_date (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetPassword <pyeitaa.raw.functions.account.GetPassword>`
            - :obj:`account.GetPasswordLayer68 <pyeitaa.raw.functions.account.GetPasswordLayer68>`
    """

    __slots__: List[str] = ["new_algo", "new_secure_algo", "secure_random", "has_recovery", "has_secure_values", "has_password", "current_algo", "srp_B", "srp_id", "hint", "email_unconfirmed_pattern", "pending_reset_date"]

    ID = 0x185b184f
    QUALNAME = "types.account.Password"

    def __init__(self, *, new_algo: "raw.base.PasswordKdfAlgo", new_secure_algo: "raw.base.SecurePasswordKdfAlgo", secure_random: bytes, has_recovery: Optional[bool] = None, has_secure_values: Optional[bool] = None, has_password: Optional[bool] = None, current_algo: "raw.base.PasswordKdfAlgo" = None, srp_B: Optional[bytes] = None, srp_id: Optional[int] = None, hint: Optional[str] = None, email_unconfirmed_pattern: Optional[str] = None, pending_reset_date: Optional[int] = None) -> None:
        self.new_algo = new_algo  # PasswordKdfAlgo
        self.new_secure_algo = new_secure_algo  # SecurePasswordKdfAlgo
        self.secure_random = secure_random  # bytes
        self.has_recovery = has_recovery  # flags.0?true
        self.has_secure_values = has_secure_values  # flags.1?true
        self.has_password = has_password  # flags.2?true
        self.current_algo = current_algo  # flags.2?PasswordKdfAlgo
        self.srp_B = srp_B  # flags.2?bytes
        self.srp_id = srp_id  # flags.2?long
        self.hint = hint  # flags.3?string
        self.email_unconfirmed_pattern = email_unconfirmed_pattern  # flags.4?string
        self.pending_reset_date = pending_reset_date  # flags.5?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        has_recovery = True if flags & (1 << 0) else False
        has_secure_values = True if flags & (1 << 1) else False
        has_password = True if flags & (1 << 2) else False
        current_algo = TLObject.read(data) if flags & (1 << 2) else None
        
        srp_B = Bytes.read(data) if flags & (1 << 2) else None
        srp_id = Long.read(data) if flags & (1 << 2) else None
        hint = String.read(data) if flags & (1 << 3) else None
        email_unconfirmed_pattern = String.read(data) if flags & (1 << 4) else None
        new_algo = TLObject.read(data)
        
        new_secure_algo = TLObject.read(data)
        
        secure_random = Bytes.read(data)
        
        pending_reset_date = Int.read(data) if flags & (1 << 5) else None
        return Password(new_algo=new_algo, new_secure_algo=new_secure_algo, secure_random=secure_random, has_recovery=has_recovery, has_secure_values=has_secure_values, has_password=has_password, current_algo=current_algo, srp_B=srp_B, srp_id=srp_id, hint=hint, email_unconfirmed_pattern=email_unconfirmed_pattern, pending_reset_date=pending_reset_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.has_recovery else 0
        flags |= (1 << 1) if self.has_secure_values else 0
        flags |= (1 << 2) if self.has_password else 0
        flags |= (1 << 2) if self.current_algo is not None else 0
        flags |= (1 << 2) if self.srp_B is not None else 0
        flags |= (1 << 2) if self.srp_id is not None else 0
        flags |= (1 << 3) if self.hint is not None else 0
        flags |= (1 << 4) if self.email_unconfirmed_pattern is not None else 0
        flags |= (1 << 5) if self.pending_reset_date is not None else 0
        data.write(Int(flags))
        
        if self.current_algo is not None:
            data.write(self.current_algo.write())
        
        if self.srp_B is not None:
            data.write(Bytes(self.srp_B))
        
        if self.srp_id is not None:
            data.write(Long(self.srp_id))
        
        if self.hint is not None:
            data.write(String(self.hint))
        
        if self.email_unconfirmed_pattern is not None:
            data.write(String(self.email_unconfirmed_pattern))
        
        data.write(self.new_algo.write())
        
        data.write(self.new_secure_algo.write())
        
        data.write(Bytes(self.secure_random))
        
        if self.pending_reset_date is not None:
            data.write(Int(self.pending_reset_date))
        
        return data.getvalue()
