from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SentCode(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.SentCode`.

    Details:
        - Layer: ``135``
        - ID: ``0x5e002502``

    Parameters:
        type: :obj:`auth.SentCodeType <pyeitaa.raw.base.auth.SentCodeType>`
        phone_code_hash: ``str``
        next_type (optional): :obj:`auth.CodeType <pyeitaa.raw.base.auth.CodeType>`
        timeout (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 6 methods:

        .. hlist::
            :columns: 2

            - :obj:`auth.SendCode <pyeitaa.raw.functions.auth.SendCode>`
            - :obj:`auth.ResendCode <pyeitaa.raw.functions.auth.ResendCode>`
            - :obj:`account.SendChangePhoneCode <pyeitaa.raw.functions.account.SendChangePhoneCode>`
            - :obj:`account.SendConfirmPhoneCode <pyeitaa.raw.functions.account.SendConfirmPhoneCode>`
            - :obj:`account.SendVerifyPhoneCode <pyeitaa.raw.functions.account.SendVerifyPhoneCode>`
            - :obj:`SendTwoStepVerificationCode <pyeitaa.raw.functions.SendTwoStepVerificationCode>`
    """

    __slots__: List[str] = ["type", "phone_code_hash", "next_type", "timeout"]

    ID = 0x5e002502
    QUALNAME = "types.auth.SentCode"

    def __init__(self, *, type: "raw.base.auth.SentCodeType", phone_code_hash: str, next_type: "raw.base.auth.CodeType" = None, timeout: Optional[int] = None) -> None:
        self.type = type  # auth.SentCodeType
        self.phone_code_hash = phone_code_hash  # string
        self.next_type = next_type  # flags.1?auth.CodeType
        self.timeout = timeout  # flags.2?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        type = TLObject.read(data)
        
        phone_code_hash = String.read(data)
        
        next_type = TLObject.read(data) if flags & (1 << 1) else None
        
        timeout = Int.read(data) if flags & (1 << 2) else None
        return SentCode(type=type, phone_code_hash=phone_code_hash, next_type=next_type, timeout=timeout)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.next_type is not None else 0
        flags |= (1 << 2) if self.timeout is not None else 0
        data.write(Int(flags))
        
        data.write(self.type.write())
        
        data.write(String(self.phone_code_hash))
        
        if self.next_type is not None:
            data.write(self.next_type.write())
        
        if self.timeout is not None:
            data.write(Int(self.timeout))
        
        return data.getvalue()
