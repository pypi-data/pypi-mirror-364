from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetDialogFilters(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xe612693``

    **No parameters required.**

    Returns:
        List of :obj:`DialogFilter <pyeitaa.raw.base.DialogFilter>`
    """

    __slots__: List[str] = []

    ID = -0xe612693
    QUALNAME = "functions.messages.GetDialogFilters"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetDialogFilters()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
