from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetPrivacy(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x252436b0``

    Parameters:
        key: :obj:`InputPrivacyKey <pyeitaa.raw.base.InputPrivacyKey>`

    Returns:
        :obj:`account.PrivacyRules <pyeitaa.raw.base.account.PrivacyRules>`
    """

    __slots__: List[str] = ["key"]

    ID = -0x252436b0
    QUALNAME = "functions.account.GetPrivacy"

    def __init__(self, *, key: "raw.base.InputPrivacyKey") -> None:
        self.key = key  # InputPrivacyKey

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        key = TLObject.read(data)
        
        return GetPrivacy(key=key)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.key.write())
        
        return data.getvalue()
