from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AccessPointRule(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.AccessPointRule`.

    Details:
        - Layer: ``135``
        - ID: ``0x4679b65f``

    Parameters:
        phone_prefix_rules: ``str``
        dc_id: ``int`` ``32-bit``
        ips: List of :obj:`IpPort <pyeitaa.raw.base.IpPort>`
    """

    __slots__: List[str] = ["phone_prefix_rules", "dc_id", "ips"]

    ID = 0x4679b65f
    QUALNAME = "types.AccessPointRule"

    def __init__(self, *, phone_prefix_rules: str, dc_id: int, ips: List["raw.base.IpPort"]) -> None:
        self.phone_prefix_rules = phone_prefix_rules  # string
        self.dc_id = dc_id  # int
        self.ips = ips  # vector<IpPort>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        phone_prefix_rules = String.read(data)
        
        dc_id = Int.read(data)
        
        ips = TLObject.read(data)
        
        return AccessPointRule(phone_prefix_rules=phone_prefix_rules, dc_id=dc_id, ips=ips)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.phone_prefix_rules))
        
        data.write(Int(self.dc_id))
        
        data.write(Vector(self.ips))
        
        return data.getvalue()
