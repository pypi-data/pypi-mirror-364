from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DestroyAuthKey(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2ebcaea0``

    **No parameters required.**

    Returns:
        :obj:`DestroyAuthKeyRes <pyeitaa.raw.base.DestroyAuthKeyRes>`
    """

    __slots__: List[str] = []

    ID = -0x2ebcaea0
    QUALNAME = "functions.DestroyAuthKey"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return DestroyAuthKey()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
