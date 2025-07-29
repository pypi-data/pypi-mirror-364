from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetAppChangelog(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6fef1091``

    Parameters:
        prev_app_version: ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["prev_app_version"]

    ID = -0x6fef1091
    QUALNAME = "functions.help.GetAppChangelog"

    def __init__(self, *, prev_app_version: str) -> None:
        self.prev_app_version = prev_app_version  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_app_version = String.read(data)
        
        return GetAppChangelog(prev_app_version=prev_app_version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.prev_app_version))
        
        return data.getvalue()
