from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PrivacyKeyPhoneNumber(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PrivacyKey`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2e651b93``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x2e651b93
    QUALNAME = "types.PrivacyKeyPhoneNumber"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return PrivacyKeyPhoneNumber()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
