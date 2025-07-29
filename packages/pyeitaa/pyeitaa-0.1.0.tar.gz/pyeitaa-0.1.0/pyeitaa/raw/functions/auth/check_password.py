from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class CheckPassword(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2e74b2ea``

    Parameters:
        password: :obj:`InputCheckPasswordSRP <pyeitaa.raw.base.InputCheckPasswordSRP>`

    Returns:
        :obj:`auth.Authorization <pyeitaa.raw.base.auth.Authorization>`
    """

    __slots__: List[str] = ["password"]

    ID = -0x2e74b2ea
    QUALNAME = "functions.auth.CheckPassword"

    def __init__(self, *, password: "raw.base.InputCheckPasswordSRP") -> None:
        self.password = password  # InputCheckPasswordSRP

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        password = TLObject.read(data)
        
        return CheckPassword(password=password)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.password.write())
        
        return data.getvalue()
