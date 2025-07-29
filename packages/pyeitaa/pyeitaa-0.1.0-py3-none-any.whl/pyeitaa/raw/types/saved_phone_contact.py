from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SavedPhoneContact(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SavedContact`.

    Details:
        - Layer: ``135``
        - ID: ``0x1142bd56``

    Parameters:
        phone: ``str``
        first_name: ``str``
        last_name: ``str``
        date: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetSaved <pyeitaa.raw.functions.contacts.GetSaved>`
    """

    __slots__: List[str] = ["phone", "first_name", "last_name", "date"]

    ID = 0x1142bd56
    QUALNAME = "types.SavedPhoneContact"

    def __init__(self, *, phone: str, first_name: str, last_name: str, date: int) -> None:
        self.phone = phone  # string
        self.first_name = first_name  # string
        self.last_name = last_name  # string
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone = String.read(data)
        
        first_name = String.read(data)
        
        last_name = String.read(data)
        
        date = Int.read(data)
        
        return SavedPhoneContact(phone=phone, first_name=first_name, last_name=last_name, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone))
        
        data.write(String(self.first_name))
        
        data.write(String(self.last_name))
        
        data.write(Int(self.date))
        
        return data.getvalue()
