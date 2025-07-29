from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ContactStatus(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ContactStatus`.

    Details:
        - Layer: ``135``
        - ID: ``0x16d9703b``

    Parameters:
        user_id: ``int`` ``64-bit``
        status: :obj:`UserStatus <pyeitaa.raw.base.UserStatus>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.GetStatuses <pyeitaa.raw.functions.contacts.GetStatuses>`
    """

    __slots__: List[str] = ["user_id", "status"]

    ID = 0x16d9703b
    QUALNAME = "types.ContactStatus"

    def __init__(self, *, user_id: int, status: "raw.base.UserStatus") -> None:
        self.user_id = user_id  # long
        self.status = status  # UserStatus

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        status = TLObject.read(data)
        
        return ContactStatus(user_id=user_id, status=status)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(self.status.write())
        
        return data.getvalue()
