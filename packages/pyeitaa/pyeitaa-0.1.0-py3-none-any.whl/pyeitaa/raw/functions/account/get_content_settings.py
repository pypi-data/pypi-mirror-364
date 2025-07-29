from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetContentSettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7464b252``

    **No parameters required.**

    Returns:
        :obj:`account.ContentSettings <pyeitaa.raw.base.account.ContentSettings>`
    """

    __slots__: List[str] = []

    ID = -0x7464b252
    QUALNAME = "functions.account.GetContentSettings"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetContentSettings()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
