from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Contacts(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.contacts.Contacts`.

    Details:
        - Layer: ``135``
        - ID: ``-0x151781be``

    Parameters:
        contacts: List of :obj:`Contact <pyeitaa.raw.base.Contact>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetContacts <pyeitaa.raw.functions.contacts.GetContacts>`
    """

    __slots__: List[str] = ["contacts", "users"]

    ID = -0x151781be
    QUALNAME = "types.contacts.Contacts"

    def __init__(self, *, contacts: List["raw.base.Contact"], users: List["raw.base.User"]) -> None:
        self.contacts = contacts  # Vector<Contact>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        contacts = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return Contacts(contacts=contacts, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.contacts))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
