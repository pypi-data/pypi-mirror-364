from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputGeoPointEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputGeoPoint`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1b3edc2a``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x1b3edc2a
    QUALNAME = "types.InputGeoPointEmpty"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return InputGeoPointEmpty()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
