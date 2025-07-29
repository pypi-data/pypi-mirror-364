from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageMediaContact(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x70322949``

    Parameters:
        phone_number: ``str``
        first_name: ``str``
        last_name: ``str``
        vcard: ``str``
        user_id: ``int`` ``64-bit``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["phone_number", "first_name", "last_name", "vcard", "user_id"]

    ID = 0x70322949
    QUALNAME = "types.MessageMediaContact"

    def __init__(self, *, phone_number: str, first_name: str, last_name: str, vcard: str, user_id: int) -> None:
        self.phone_number = phone_number  # string
        self.first_name = first_name  # string
        self.last_name = last_name  # string
        self.vcard = vcard  # string
        self.user_id = user_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_number = String.read(data)
        
        first_name = String.read(data)
        
        last_name = String.read(data)
        
        vcard = String.read(data)
        
        user_id = Long.read(data)
        
        return MessageMediaContact(phone_number=phone_number, first_name=first_name, last_name=last_name, vcard=vcard, user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone_number))
        
        data.write(String(self.first_name))
        
        data.write(String(self.last_name))
        
        data.write(String(self.vcard))
        
        data.write(Long(self.user_id))
        
        return data.getvalue()
