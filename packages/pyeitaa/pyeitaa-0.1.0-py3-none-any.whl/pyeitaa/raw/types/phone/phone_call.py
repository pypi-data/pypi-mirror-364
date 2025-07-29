from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PhoneCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.phone.PhoneCall`.

    Details:
        - Layer: ``135``
        - ID: ``-0x137d1ec0``

    Parameters:
        phone_call: :obj:`PhoneCall <pyeitaa.raw.base.PhoneCall>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`phone.RequestCall <pyeitaa.raw.functions.phone.RequestCall>`
            - :obj:`phone.AcceptCall <pyeitaa.raw.functions.phone.AcceptCall>`
            - :obj:`phone.ConfirmCall <pyeitaa.raw.functions.phone.ConfirmCall>`
    """

    __slots__: List[str] = ["phone_call", "users"]

    ID = -0x137d1ec0
    QUALNAME = "types.phone.PhoneCall"

    def __init__(self, *, phone_call: "raw.base.PhoneCall", users: List["raw.base.User"]) -> None:
        self.phone_call = phone_call  # PhoneCall
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_call = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return PhoneCall(phone_call=phone_call, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.phone_call.write())
        
        data.write(Vector(self.users))
        
        return data.getvalue()
