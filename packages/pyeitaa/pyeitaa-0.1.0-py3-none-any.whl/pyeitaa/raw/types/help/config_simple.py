from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ConfigSimple(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.ConfigSimple`.

    Details:
        - Layer: ``135``
        - ID: ``0x5a592a6c``

    Parameters:
        date: ``int`` ``32-bit``
        expires: ``int`` ``32-bit``
        rules: List of :obj:`AccessPointRule <pyeitaa.raw.base.AccessPointRule>`
    """

    __slots__: List[str] = ["date", "expires", "rules"]

    ID = 0x5a592a6c
    QUALNAME = "types.help.ConfigSimple"

    def __init__(self, *, date: int, expires: int, rules: List["raw.base.AccessPointRule"]) -> None:
        self.date = date  # int
        self.expires = expires  # int
        self.rules = rules  # vector<AccessPointRule>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        date = Int.read(data)
        
        expires = Int.read(data)
        
        rules = TLObject.read(data)
        
        return ConfigSimple(date=date, expires=expires, rules=rules)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.date))
        
        data.write(Int(self.expires))
        
        data.write(Vector(self.rules))
        
        return data.getvalue()
