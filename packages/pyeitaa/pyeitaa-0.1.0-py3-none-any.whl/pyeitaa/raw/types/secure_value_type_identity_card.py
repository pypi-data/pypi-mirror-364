from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SecureValueTypeIdentityCard(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureValueType`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5f2f8bb5``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x5f2f8bb5
    QUALNAME = "types.SecureValueTypeIdentityCard"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return SecureValueTypeIdentityCard()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
