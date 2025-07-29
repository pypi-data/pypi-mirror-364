from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CheckedHistoryImportPeer(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.CheckedHistoryImportPeer`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5db218e9``

    Parameters:
        confirm_text: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.CheckHistoryImportPeer <pyeitaa.raw.functions.messages.CheckHistoryImportPeer>`
    """

    __slots__: List[str] = ["confirm_text"]

    ID = -0x5db218e9
    QUALNAME = "types.messages.CheckedHistoryImportPeer"

    def __init__(self, *, confirm_text: str) -> None:
        self.confirm_text = confirm_text  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        confirm_text = String.read(data)
        
        return CheckedHistoryImportPeer(confirm_text=confirm_text)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.confirm_text))
        
        return data.getvalue()
