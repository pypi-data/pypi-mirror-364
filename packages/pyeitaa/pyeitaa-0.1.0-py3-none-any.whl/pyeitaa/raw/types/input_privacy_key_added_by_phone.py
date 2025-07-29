from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputPrivacyKeyAddedByPhone(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputPrivacyKey`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2ede6423``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x2ede6423
    QUALNAME = "types.InputPrivacyKeyAddedByPhone"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return InputPrivacyKeyAddedByPhone()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
