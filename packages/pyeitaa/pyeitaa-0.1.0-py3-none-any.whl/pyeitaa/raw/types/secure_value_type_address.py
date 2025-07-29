from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SecureValueTypeAddress(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureValueType`.

    Details:
        - Layer: ``135``
        - ID: ``-0x341ce1da``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x341ce1da
    QUALNAME = "types.SecureValueTypeAddress"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return SecureValueTypeAddress()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
