from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ContactsNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.contacts.Contacts`.

    Details:
        - Layer: ``135``
        - ID: ``-0x48b4562e``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetContacts <pyeitaa.raw.functions.contacts.GetContacts>`
    """

    __slots__: List[str] = []

    ID = -0x48b4562e
    QUALNAME = "types.contacts.ContactsNotModified"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return ContactsNotModified()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
