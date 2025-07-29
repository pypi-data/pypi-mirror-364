from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CheckHistoryImport(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x43fe19f3``

    Parameters:
        import_head: ``str``

    Returns:
        :obj:`messages.HistoryImportParsed <pyeitaa.raw.base.messages.HistoryImportParsed>`
    """

    __slots__: List[str] = ["import_head"]

    ID = 0x43fe19f3
    QUALNAME = "functions.messages.CheckHistoryImport"

    def __init__(self, *, import_head: str) -> None:
        self.import_head = import_head  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        import_head = String.read(data)
        
        return CheckHistoryImport(import_head=import_head)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.import_head))
        
        return data.getvalue()
