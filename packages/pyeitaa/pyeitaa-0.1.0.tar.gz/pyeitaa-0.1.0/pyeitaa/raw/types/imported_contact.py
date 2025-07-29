from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ImportedContact(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ImportedContact`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3ec1c3b0``

    Parameters:
        user_id: ``int`` ``64-bit``
        client_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["user_id", "client_id"]

    ID = -0x3ec1c3b0
    QUALNAME = "types.ImportedContact"

    def __init__(self, *, user_id: int, client_id: int) -> None:
        self.user_id = user_id  # long
        self.client_id = client_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        client_id = Long.read(data)
        
        return ImportedContact(user_id=user_id, client_id=client_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Long(self.client_id))
        
        return data.getvalue()
