from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class WebAuthorizations(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.WebAuthorizations`.

    Details:
        - Layer: ``135``
        - ID: ``-0x12a93604``

    Parameters:
        authorizations: List of :obj:`WebAuthorization <pyeitaa.raw.base.WebAuthorization>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetWebAuthorizations <pyeitaa.raw.functions.account.GetWebAuthorizations>`
    """

    __slots__: List[str] = ["authorizations", "users"]

    ID = -0x12a93604
    QUALNAME = "types.account.WebAuthorizations"

    def __init__(self, *, authorizations: List["raw.base.WebAuthorization"], users: List["raw.base.User"]) -> None:
        self.authorizations = authorizations  # Vector<WebAuthorization>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        authorizations = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return WebAuthorizations(authorizations=authorizations, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.authorizations))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
