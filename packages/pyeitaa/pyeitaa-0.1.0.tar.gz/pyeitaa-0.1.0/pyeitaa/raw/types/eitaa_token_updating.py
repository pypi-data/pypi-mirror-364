from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EitaaTokenUpdating(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EitaaTokenUpdating`.

    Details:
        - Layer: ``135``
        - ID: ``-0x23dadc8b``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`EitaaTokenUpdating <pyeitaa.raw.functions.EitaaTokenUpdating>`
    """

    __slots__: List[str] = []

    ID = -0x23dadc8b
    QUALNAME = "types.EitaaTokenUpdating"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return EitaaTokenUpdating()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
