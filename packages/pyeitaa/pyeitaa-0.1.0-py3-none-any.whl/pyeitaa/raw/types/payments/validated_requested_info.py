from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ValidatedRequestedInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.payments.ValidatedRequestedInfo`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2ebae77d``

    Parameters:
        id (optional): ``str``
        shipping_options (optional): List of :obj:`ShippingOption <pyeitaa.raw.base.ShippingOption>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.ValidateRequestedInfo <pyeitaa.raw.functions.payments.ValidateRequestedInfo>`
    """

    __slots__: List[str] = ["id", "shipping_options"]

    ID = -0x2ebae77d
    QUALNAME = "types.payments.ValidatedRequestedInfo"

    def __init__(self, *, id: Optional[str] = None, shipping_options: Optional[List["raw.base.ShippingOption"]] = None) -> None:
        self.id = id  # flags.0?string
        self.shipping_options = shipping_options  # flags.1?Vector<ShippingOption>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = String.read(data) if flags & (1 << 0) else None
        shipping_options = TLObject.read(data) if flags & (1 << 1) else []
        
        return ValidatedRequestedInfo(id=id, shipping_options=shipping_options)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.id is not None else 0
        flags |= (1 << 1) if self.shipping_options is not None else 0
        data.write(Int(flags))
        
        if self.id is not None:
            data.write(String(self.id))
        
        if self.shipping_options is not None:
            data.write(Vector(self.shipping_options))
        
        return data.getvalue()
