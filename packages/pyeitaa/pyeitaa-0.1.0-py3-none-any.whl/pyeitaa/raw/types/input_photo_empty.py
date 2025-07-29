from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputPhotoEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputPhoto`.

    Details:
        - Layer: ``135``
        - ID: ``0x1cd7bf0d``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = 0x1cd7bf0d
    QUALNAME = "types.InputPhotoEmpty"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return InputPhotoEmpty()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
