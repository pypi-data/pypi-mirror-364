from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SaveDeveloperInfo(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x9a5f6e95``

    Parameters:
        vk_id: ``int`` ``32-bit``
        name: ``str``
        phone_number: ``str``
        age: ``int`` ``32-bit``
        city: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["vk_id", "name", "phone_number", "age", "city"]

    ID = 0x9a5f6e95
    QUALNAME = "functions.contest.SaveDeveloperInfo"

    def __init__(self, *, vk_id: int, name: str, phone_number: str, age: int, city: str) -> None:
        self.vk_id = vk_id  # int
        self.name = name  # string
        self.phone_number = phone_number  # string
        self.age = age  # int
        self.city = city  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        vk_id = Int.read(data)
        
        name = String.read(data)
        
        phone_number = String.read(data)
        
        age = Int.read(data)
        
        city = String.read(data)
        
        return SaveDeveloperInfo(vk_id=vk_id, name=name, phone_number=phone_number, age=age, city=city)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.vk_id))
        
        data.write(String(self.name))
        
        data.write(String(self.phone_number))
        
        data.write(Int(self.age))
        
        data.write(String(self.city))
        
        return data.getvalue()
