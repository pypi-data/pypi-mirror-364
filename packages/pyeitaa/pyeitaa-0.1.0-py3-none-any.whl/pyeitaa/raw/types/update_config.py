from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateConfig(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5dd622fa``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x5dd622fa
    QUALNAME = "types.UpdateConfig"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return UpdateConfig()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
