from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class SetContentSettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4a8b4e95``

    Parameters:
        sensitive_enabled (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["sensitive_enabled"]

    ID = -0x4a8b4e95
    QUALNAME = "functions.account.SetContentSettings"

    def __init__(self, *, sensitive_enabled: Optional[bool] = None) -> None:
        self.sensitive_enabled = sensitive_enabled  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        sensitive_enabled = True if flags & (1 << 0) else False
        return SetContentSettings(sensitive_enabled=sensitive_enabled)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.sensitive_enabled else 0
        data.write(Int(flags))
        
        return data.getvalue()
