from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Support(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.Support`.

    Details:
        - Layer: ``135``
        - ID: ``0x17c6b5f6``

    Parameters:
        phone_number: ``str``
        user: :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetSupport <pyeitaa.raw.functions.help.GetSupport>`
    """

    __slots__: List[str] = ["phone_number", "user"]

    ID = 0x17c6b5f6
    QUALNAME = "types.help.Support"

    def __init__(self, *, phone_number: str, user: "raw.base.User") -> None:
        self.phone_number = phone_number  # string
        self.user = user  # User

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_number = String.read(data)
        
        user = TLObject.read(data)
        
        return Support(phone_number=phone_number, user=user)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone_number))
        
        data.write(self.user.write())
        
        return data.getvalue()
