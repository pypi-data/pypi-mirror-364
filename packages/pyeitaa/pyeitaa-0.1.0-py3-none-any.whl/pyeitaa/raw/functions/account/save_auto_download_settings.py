from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SaveAutoDownloadSettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x76f36233``

    Parameters:
        settings: :obj:`AutoDownloadSettings <pyeitaa.raw.base.AutoDownloadSettings>`
        low (optional): ``bool``
        high (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["settings", "low", "high"]

    ID = 0x76f36233
    QUALNAME = "functions.account.SaveAutoDownloadSettings"

    def __init__(self, *, settings: "raw.base.AutoDownloadSettings", low: Optional[bool] = None, high: Optional[bool] = None) -> None:
        self.settings = settings  # AutoDownloadSettings
        self.low = low  # flags.0?true
        self.high = high  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        low = True if flags & (1 << 0) else False
        high = True if flags & (1 << 1) else False
        settings = TLObject.read(data)
        
        return SaveAutoDownloadSettings(settings=settings, low=low, high=high)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.low else 0
        flags |= (1 << 1) if self.high else 0
        data.write(Int(flags))
        
        data.write(self.settings.write())
        
        return data.getvalue()
