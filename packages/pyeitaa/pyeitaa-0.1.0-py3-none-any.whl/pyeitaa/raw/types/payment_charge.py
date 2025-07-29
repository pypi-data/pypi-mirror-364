from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PaymentCharge(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PaymentCharge`.

    Details:
        - Layer: ``135``
        - ID: ``-0x15fd3d82``

    Parameters:
        id: ``str``
        provider_charge_id: ``str``
    """

    __slots__: List[str] = ["id", "provider_charge_id"]

    ID = -0x15fd3d82
    QUALNAME = "types.PaymentCharge"

    def __init__(self, *, id: str, provider_charge_id: str) -> None:
        self.id = id  # string
        self.provider_charge_id = provider_charge_id  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = String.read(data)
        
        provider_charge_id = String.read(data)
        
        return PaymentCharge(id=id, provider_charge_id=provider_charge_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.id))
        
        data.write(String(self.provider_charge_id))
        
        return data.getvalue()
