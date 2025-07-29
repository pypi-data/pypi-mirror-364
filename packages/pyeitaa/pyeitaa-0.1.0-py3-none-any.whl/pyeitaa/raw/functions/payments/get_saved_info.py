from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetSavedInfo(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x227d824b``

    **No parameters required.**

    Returns:
        :obj:`payments.SavedInfo <pyeitaa.raw.base.payments.SavedInfo>`
    """

    __slots__: List[str] = []

    ID = 0x227d824b
    QUALNAME = "functions.payments.GetSavedInfo"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetSavedInfo()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
