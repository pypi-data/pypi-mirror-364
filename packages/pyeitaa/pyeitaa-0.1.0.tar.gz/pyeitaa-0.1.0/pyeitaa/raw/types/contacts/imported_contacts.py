from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ImportedContacts(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.contacts.ImportedContacts`.

    Details:
        - Layer: ``135``
        - ID: ``0x77d01c3b``

    Parameters:
        imported: List of :obj:`ImportedContact <pyeitaa.raw.base.ImportedContact>`
        popular_invites: List of :obj:`PopularContact <pyeitaa.raw.base.PopularContact>`
        retry_contacts: List of ``int`` ``64-bit``
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.ImportContacts <pyeitaa.raw.functions.contacts.ImportContacts>`
    """

    __slots__: List[str] = ["imported", "popular_invites", "retry_contacts", "users"]

    ID = 0x77d01c3b
    QUALNAME = "types.contacts.ImportedContacts"

    def __init__(self, *, imported: List["raw.base.ImportedContact"], popular_invites: List["raw.base.PopularContact"], retry_contacts: List[int], users: List["raw.base.User"]) -> None:
        self.imported = imported  # Vector<ImportedContact>
        self.popular_invites = popular_invites  # Vector<PopularContact>
        self.retry_contacts = retry_contacts  # Vector<long>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        imported = TLObject.read(data)
        
        popular_invites = TLObject.read(data)
        
        retry_contacts = TLObject.read(data, Long)
        
        users = TLObject.read(data)
        
        return ImportedContacts(imported=imported, popular_invites=popular_invites, retry_contacts=retry_contacts, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.imported))
        
        data.write(Vector(self.popular_invites))
        
        data.write(Vector(self.retry_contacts, Long))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
