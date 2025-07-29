from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PrivacyKeyProfilePhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PrivacyKey`.

    Details:
        - Layer: ``135``
        - ID: ``-0x69eae013``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x69eae013
    QUALNAME = "types.PrivacyKeyProfilePhoto"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return PrivacyKeyProfilePhoto()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
