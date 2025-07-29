from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetSaved(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7d0e1c61``

    **No parameters required.**

    Returns:
        List of :obj:`SavedContact <pyeitaa.raw.base.SavedContact>`
    """

    __slots__: List[str] = []

    ID = -0x7d0e1c61
    QUALNAME = "functions.contacts.GetSaved"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetSaved()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
