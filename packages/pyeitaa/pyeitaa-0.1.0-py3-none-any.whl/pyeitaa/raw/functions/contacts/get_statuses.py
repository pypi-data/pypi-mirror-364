from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetStatuses(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3b5cac12``

    **No parameters required.**

    Returns:
        List of :obj:`ContactStatus <pyeitaa.raw.base.ContactStatus>`
    """

    __slots__: List[str] = []

    ID = -0x3b5cac12
    QUALNAME = "functions.contacts.GetStatuses"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetStatuses()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
