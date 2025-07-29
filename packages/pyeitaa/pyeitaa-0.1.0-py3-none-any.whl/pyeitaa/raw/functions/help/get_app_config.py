from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetAppConfig(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x676ebef0``

    **No parameters required.**

    Returns:
        :obj:`JSONValue <pyeitaa.raw.base.JSONValue>`
    """

    __slots__: List[str] = []

    ID = -0x676ebef0
    QUALNAME = "functions.help.GetAppConfig"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetAppConfig()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
