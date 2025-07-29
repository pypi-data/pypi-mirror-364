from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class AddContact(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x170b9c30``

    Parameters:
        id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        first_name: ``str``
        last_name: ``str``
        phone: ``str``
        add_phone_privacy_exception (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["id", "first_name", "last_name", "phone", "add_phone_privacy_exception"]

    ID = -0x170b9c30
    QUALNAME = "functions.contacts.AddContact"

    def __init__(self, *, id: "raw.base.InputUser", first_name: str, last_name: str, phone: str, add_phone_privacy_exception: Optional[bool] = None) -> None:
        self.id = id  # InputUser
        self.first_name = first_name  # string
        self.last_name = last_name  # string
        self.phone = phone  # string
        self.add_phone_privacy_exception = add_phone_privacy_exception  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        add_phone_privacy_exception = True if flags & (1 << 0) else False
        id = TLObject.read(data)
        
        first_name = String.read(data)
        
        last_name = String.read(data)
        
        phone = String.read(data)
        
        return AddContact(id=id, first_name=first_name, last_name=last_name, phone=phone, add_phone_privacy_exception=add_phone_privacy_exception)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.add_phone_privacy_exception else 0
        data.write(Int(flags))
        
        data.write(self.id.write())
        
        data.write(String(self.first_name))
        
        data.write(String(self.last_name))
        
        data.write(String(self.phone))
        
        return data.getvalue()
