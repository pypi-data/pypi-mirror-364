from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetGlobalPrivacySettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1edaaac2``

    Parameters:
        settings: :obj:`GlobalPrivacySettings <pyeitaa.raw.base.GlobalPrivacySettings>`

    Returns:
        :obj:`GlobalPrivacySettings <pyeitaa.raw.base.GlobalPrivacySettings>`
    """

    __slots__: List[str] = ["settings"]

    ID = 0x1edaaac2
    QUALNAME = "functions.account.SetGlobalPrivacySettings"

    def __init__(self, *, settings: "raw.base.GlobalPrivacySettings") -> None:
        self.settings = settings  # GlobalPrivacySettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        settings = TLObject.read(data)
        
        return SetGlobalPrivacySettings(settings=settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.settings.write())
        
        return data.getvalue()
