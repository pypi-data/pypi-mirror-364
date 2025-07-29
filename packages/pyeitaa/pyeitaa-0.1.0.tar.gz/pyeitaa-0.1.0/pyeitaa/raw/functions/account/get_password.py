from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetPassword(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x548a30f5``

    **No parameters required.**

    Returns:
        :obj:`account.Password <pyeitaa.raw.base.account.Password>`
    """

    __slots__: List[str] = []

    ID = 0x548a30f5
    QUALNAME = "functions.account.GetPassword"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetPassword()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
