from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EitaaUpdatesExpireToken(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EitaaUpdatesExpireToken`.

    Details:
        - Layer: ``135``
        - ID: ``-0x23dadc87``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`EitaaUpdatesExpireToken <pyeitaa.raw.functions.EitaaUpdatesExpireToken>`
    """

    __slots__: List[str] = []

    ID = -0x23dadc87
    QUALNAME = "types.EitaaUpdatesExpireToken"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return EitaaUpdatesExpireToken()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
