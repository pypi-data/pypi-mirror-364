from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DestroyAuthKeyNone(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DestroyAuthKeyRes`.

    Details:
        - Layer: ``135``
        - ID: ``0xa9f2259``

    **No parameters required.**

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`DestroyAuthKey <pyeitaa.raw.functions.DestroyAuthKey>`
            - :obj:`DestroyAuthKey <pyeitaa.raw.functions.DestroyAuthKey>`
    """

    __slots__: List[str] = []

    ID = 0xa9f2259
    QUALNAME = "types.DestroyAuthKeyNone"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return DestroyAuthKeyNone()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
