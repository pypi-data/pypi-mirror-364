from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputUserEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputUser`.

    Details:
        - Layer: ``135``
        - ID: ``-0x46777931``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x46777931
    QUALNAME = "types.InputUserEmpty"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return InputUserEmpty()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
