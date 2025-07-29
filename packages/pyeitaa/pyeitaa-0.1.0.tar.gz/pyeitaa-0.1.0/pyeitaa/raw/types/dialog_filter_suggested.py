from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DialogFilterSuggested(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DialogFilterSuggested`.

    Details:
        - Layer: ``135``
        - ID: ``0x77744d4a``

    Parameters:
        filter: :obj:`DialogFilter <pyeitaa.raw.base.DialogFilter>`
        description: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetSuggestedDialogFilters <pyeitaa.raw.functions.messages.GetSuggestedDialogFilters>`
    """

    __slots__: List[str] = ["filter", "description"]

    ID = 0x77744d4a
    QUALNAME = "types.DialogFilterSuggested"

    def __init__(self, *, filter: "raw.base.DialogFilter", description: str) -> None:
        self.filter = filter  # DialogFilter
        self.description = description  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        filter = TLObject.read(data)
        
        description = String.read(data)
        
        return DialogFilterSuggested(filter=filter, description=description)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.filter.write())
        
        data.write(String(self.description))
        
        return data.getvalue()
