from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetAllSecureValues(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4d774383``

    **No parameters required.**

    Returns:
        List of :obj:`SecureValue <pyeitaa.raw.base.SecureValue>`
    """

    __slots__: List[str] = []

    ID = -0x4d774383
    QUALNAME = "functions.account.GetAllSecureValues"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetAllSecureValues()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
