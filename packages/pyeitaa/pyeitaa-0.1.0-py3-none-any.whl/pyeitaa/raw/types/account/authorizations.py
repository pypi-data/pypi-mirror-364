from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Authorizations(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.Authorizations`.

    Details:
        - Layer: ``135``
        - ID: ``0x1250abde``

    Parameters:
        authorizations: List of :obj:`Authorization <pyeitaa.raw.base.Authorization>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAuthorizations <pyeitaa.raw.functions.account.GetAuthorizations>`
    """

    __slots__: List[str] = ["authorizations"]

    ID = 0x1250abde
    QUALNAME = "types.account.Authorizations"

    def __init__(self, *, authorizations: List["raw.base.Authorization"]) -> None:
        self.authorizations = authorizations  # Vector<Authorization>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        authorizations = TLObject.read(data)
        
        return Authorizations(authorizations=authorizations)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.authorizations))
        
        return data.getvalue()
