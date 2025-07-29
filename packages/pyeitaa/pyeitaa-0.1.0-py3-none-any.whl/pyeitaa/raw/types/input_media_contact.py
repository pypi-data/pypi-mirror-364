from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputMediaContact(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7548205``

    Parameters:
        phone_number: ``str``
        first_name: ``str``
        last_name: ``str``
        vcard: ``str``
    """

    __slots__: List[str] = ["phone_number", "first_name", "last_name", "vcard"]

    ID = -0x7548205
    QUALNAME = "types.InputMediaContact"

    def __init__(self, *, phone_number: str, first_name: str, last_name: str, vcard: str) -> None:
        self.phone_number = phone_number  # string
        self.first_name = first_name  # string
        self.last_name = last_name  # string
        self.vcard = vcard  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_number = String.read(data)
        
        first_name = String.read(data)
        
        last_name = String.read(data)
        
        vcard = String.read(data)
        
        return InputMediaContact(phone_number=phone_number, first_name=first_name, last_name=last_name, vcard=vcard)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone_number))
        
        data.write(String(self.first_name))
        
        data.write(String(self.last_name))
        
        data.write(String(self.vcard))
        
        return data.getvalue()
