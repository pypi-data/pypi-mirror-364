from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetPrivacy(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3607e318``

    Parameters:
        key: :obj:`InputPrivacyKey <pyeitaa.raw.base.InputPrivacyKey>`
        rules: List of :obj:`InputPrivacyRule <pyeitaa.raw.base.InputPrivacyRule>`

    Returns:
        :obj:`account.PrivacyRules <pyeitaa.raw.base.account.PrivacyRules>`
    """

    __slots__: List[str] = ["key", "rules"]

    ID = -0x3607e318
    QUALNAME = "functions.account.SetPrivacy"

    def __init__(self, *, key: "raw.base.InputPrivacyKey", rules: List["raw.base.InputPrivacyRule"]) -> None:
        self.key = key  # InputPrivacyKey
        self.rules = rules  # Vector<InputPrivacyRule>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        key = TLObject.read(data)
        
        rules = TLObject.read(data)
        
        return SetPrivacy(key=key, rules=rules)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.key.write())
        
        data.write(Vector(self.rules))
        
        return data.getvalue()
