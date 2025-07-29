from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdatePrivacy(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x11c4d8d6``

    Parameters:
        key: :obj:`PrivacyKey <pyeitaa.raw.base.PrivacyKey>`
        rules: List of :obj:`PrivacyRule <pyeitaa.raw.base.PrivacyRule>`
    """

    __slots__: List[str] = ["key", "rules"]

    ID = -0x11c4d8d6
    QUALNAME = "types.UpdatePrivacy"

    def __init__(self, *, key: "raw.base.PrivacyKey", rules: List["raw.base.PrivacyRule"]) -> None:
        self.key = key  # PrivacyKey
        self.rules = rules  # Vector<PrivacyRule>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        key = TLObject.read(data)
        
        rules = TLObject.read(data)
        
        return UpdatePrivacy(key=key, rules=rules)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.key.write())
        
        data.write(Vector(self.rules))
        
        return data.getvalue()
