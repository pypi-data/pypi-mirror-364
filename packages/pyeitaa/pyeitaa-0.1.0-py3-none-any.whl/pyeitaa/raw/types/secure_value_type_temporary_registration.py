from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SecureValueTypeTemporaryRegistration(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureValueType`.

    Details:
        - Layer: ``135``
        - ID: ``-0x15fd13cd``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x15fd13cd
    QUALNAME = "types.SecureValueTypeTemporaryRegistration"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return SecureValueTypeTemporaryRegistration()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
