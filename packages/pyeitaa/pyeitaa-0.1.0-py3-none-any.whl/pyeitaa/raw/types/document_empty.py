from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DocumentEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Document`.

    Details:
        - Layer: ``135``
        - ID: ``0x36f8c871``

    Parameters:
        id: ``int`` ``64-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.UploadTheme <pyeitaa.raw.functions.account.UploadTheme>`
            - :obj:`messages.GetDocumentByHash <pyeitaa.raw.functions.messages.GetDocumentByHash>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x36f8c871
    QUALNAME = "types.DocumentEmpty"

    def __init__(self, *, id: int) -> None:
        self.id = id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        return DocumentEmpty(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        return data.getvalue()
