from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetDeepLinkInfo(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3fedc75f``

    Parameters:
        path: ``str``

    Returns:
        :obj:`help.DeepLinkInfo <pyeitaa.raw.base.help.DeepLinkInfo>`
    """

    __slots__: List[str] = ["path"]

    ID = 0x3fedc75f
    QUALNAME = "functions.help.GetDeepLinkInfo"

    def __init__(self, *, path: str) -> None:
        self.path = path  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        path = String.read(data)
        
        return GetDeepLinkInfo(path=path)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.path))
        
        return data.getvalue()
