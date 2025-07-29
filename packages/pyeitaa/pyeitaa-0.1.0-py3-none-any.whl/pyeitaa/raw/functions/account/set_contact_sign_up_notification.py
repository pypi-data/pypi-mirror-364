from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SetContactSignUpNotification(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x300bc09f``

    Parameters:
        silent: ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["silent"]

    ID = -0x300bc09f
    QUALNAME = "functions.account.SetContactSignUpNotification"

    def __init__(self, *, silent: bool) -> None:
        self.silent = silent  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        silent = Bool.read(data)
        
        return SetContactSignUpNotification(silent=silent)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bool(self.silent))
        
        return data.getvalue()
