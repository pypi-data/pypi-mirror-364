from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResetNotifySettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2481e8b9``

    **No parameters required.**

    Returns:
        ``bool``
    """

    __slots__: List[str] = []

    ID = -0x2481e8b9
    QUALNAME = "functions.account.ResetNotifySettings"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return ResetNotifySettings()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
