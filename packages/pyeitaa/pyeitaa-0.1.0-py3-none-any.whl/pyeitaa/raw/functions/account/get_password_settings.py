from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetPasswordSettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x632b1507``

    Parameters:
        password: :obj:`InputCheckPasswordSRP <pyeitaa.raw.base.InputCheckPasswordSRP>`

    Returns:
        :obj:`account.PasswordSettings <pyeitaa.raw.base.account.PasswordSettings>`
    """

    __slots__: List[str] = ["password"]

    ID = -0x632b1507
    QUALNAME = "functions.account.GetPasswordSettings"

    def __init__(self, *, password: "raw.base.InputCheckPasswordSRP") -> None:
        self.password = password  # InputCheckPasswordSRP

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        password = TLObject.read(data)
        
        return GetPasswordSettings(password=password)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.password.write())
        
        return data.getvalue()
