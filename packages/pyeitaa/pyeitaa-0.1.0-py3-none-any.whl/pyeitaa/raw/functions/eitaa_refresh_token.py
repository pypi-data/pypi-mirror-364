from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EitaaRefreshToken(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x23badc97``

    Parameters:
        app_info: :obj:`EitaaAppInfo <pyeitaa.raw.base.EitaaAppInfo>`

    Returns:
        :obj:`EitaaRefreshToken <pyeitaa.raw.base.EitaaRefreshToken>`
    """

    __slots__: List[str] = ["app_info"]

    ID = -0x23badc97
    QUALNAME = "functions.EitaaRefreshToken"

    def __init__(self, *, app_info: "raw.base.EitaaAppInfo") -> None:
        self.app_info = app_info  # EitaaAppInfo

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        app_info = TLObject.read(data)
        
        return EitaaRefreshToken(app_info=app_info)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.app_info.write())
        
        return data.getvalue()
