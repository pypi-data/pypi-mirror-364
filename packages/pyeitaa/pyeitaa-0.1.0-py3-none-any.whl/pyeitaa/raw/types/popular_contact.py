from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PopularContact(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PopularContact`.

    Details:
        - Layer: ``135``
        - ID: ``0x5ce14175``

    Parameters:
        client_id: ``int`` ``64-bit``
        importers: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["client_id", "importers"]

    ID = 0x5ce14175
    QUALNAME = "types.PopularContact"

    def __init__(self, *, client_id: int, importers: int) -> None:
        self.client_id = client_id  # long
        self.importers = importers  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        client_id = Long.read(data)
        
        importers = Int.read(data)
        
        return PopularContact(client_id=client_id, importers=importers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.client_id))
        
        data.write(Int(self.importers))
        
        return data.getvalue()
