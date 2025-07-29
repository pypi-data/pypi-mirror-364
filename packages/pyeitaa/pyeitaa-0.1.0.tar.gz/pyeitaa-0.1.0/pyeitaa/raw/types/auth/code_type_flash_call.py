from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CodeTypeFlashCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.CodeType`.

    Details:
        - Layer: ``135``
        - ID: ``0x226ccefb``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = 0x226ccefb
    QUALNAME = "types.auth.CodeTypeFlashCall"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return CodeTypeFlashCall()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
