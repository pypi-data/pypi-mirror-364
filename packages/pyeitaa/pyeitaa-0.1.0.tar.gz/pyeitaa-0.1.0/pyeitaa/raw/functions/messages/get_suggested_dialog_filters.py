from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetSuggestedDialogFilters(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5d632bd4``

    **No parameters required.**

    Returns:
        List of :obj:`DialogFilterSuggested <pyeitaa.raw.base.DialogFilterSuggested>`
    """

    __slots__: List[str] = []

    ID = -0x5d632bd4
    QUALNAME = "functions.messages.GetSuggestedDialogFilters"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetSuggestedDialogFilters()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
