from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ImportContacts(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2c800be5``

    Parameters:
        contacts: List of :obj:`InputContact <pyeitaa.raw.base.InputContact>`

    Returns:
        :obj:`contacts.ImportedContacts <pyeitaa.raw.base.contacts.ImportedContacts>`
    """

    __slots__: List[str] = ["contacts"]

    ID = 0x2c800be5
    QUALNAME = "functions.contacts.ImportContacts"

    def __init__(self, *, contacts: List["raw.base.InputContact"]) -> None:
        self.contacts = contacts  # Vector<InputContact>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        contacts = TLObject.read(data)
        
        return ImportContacts(contacts=contacts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.contacts))
        
        return data.getvalue()
