from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdatePasswordSettingsLayer68(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x583b47a``

    Parameters:
        current_password_hash: ``bytes``
        new_settings: :obj:`account.PasswordInputSettings <pyeitaa.raw.base.account.PasswordInputSettings>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["current_password_hash", "new_settings"]

    ID = -0x583b47a
    QUALNAME = "functions.account.UpdatePasswordSettingsLayer68"

    def __init__(self, *, current_password_hash: bytes, new_settings: "raw.base.account.PasswordInputSettings") -> None:
        self.current_password_hash = current_password_hash  # bytes
        self.new_settings = new_settings  # account.PasswordInputSettings

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        current_password_hash = Bytes.read(data)
        
        new_settings = TLObject.read(data)
        
        return UpdatePasswordSettingsLayer68(current_password_hash=current_password_hash, new_settings=new_settings)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.current_password_hash))
        
        data.write(self.new_settings.write())
        
        return data.getvalue()
