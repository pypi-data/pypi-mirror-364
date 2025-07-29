from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EitaaUpdatesExpireToken(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x23dadc87``

    **No parameters required.**

    Returns:
        :obj:`EitaaUpdatesExpireToken <pyeitaa.raw.base.EitaaUpdatesExpireToken>`
    """

    __slots__: List[str] = []

    ID = -0x23dadc87
    QUALNAME = "functions.EitaaUpdatesExpireToken"

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
