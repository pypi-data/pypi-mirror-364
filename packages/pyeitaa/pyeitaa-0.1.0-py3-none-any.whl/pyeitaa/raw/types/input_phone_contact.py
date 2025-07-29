from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputPhoneContact(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputContact`.

    Details:
        - Layer: ``135``
        - ID: ``-0xc6d480c``

    Parameters:
        client_id: ``int`` ``64-bit``
        phone: ``str``
        first_name: ``str``
        last_name: ``str``
    """

    __slots__: List[str] = ["client_id", "phone", "first_name", "last_name"]

    ID = -0xc6d480c
    QUALNAME = "types.InputPhoneContact"

    def __init__(self, *, client_id: int, phone: str, first_name: str, last_name: str) -> None:
        self.client_id = client_id  # long
        self.phone = phone  # string
        self.first_name = first_name  # string
        self.last_name = last_name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        client_id = Long.read(data)
        
        phone = String.read(data)
        
        first_name = String.read(data)
        
        last_name = String.read(data)
        
        return InputPhoneContact(client_id=client_id, phone=phone, first_name=first_name, last_name=last_name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.client_id))
        
        data.write(String(self.phone))
        
        data.write(String(self.first_name))
        
        data.write(String(self.last_name))
        
        return data.getvalue()
