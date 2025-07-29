from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SecureRequiredType(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureRequiredType`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7d626626``

    Parameters:
        type: :obj:`SecureValueType <pyeitaa.raw.base.SecureValueType>`
        native_names (optional): ``bool``
        selfie_required (optional): ``bool``
        translation_required (optional): ``bool``
    """

    __slots__: List[str] = ["type", "native_names", "selfie_required", "translation_required"]

    ID = -0x7d626626
    QUALNAME = "types.SecureRequiredType"

    def __init__(self, *, type: "raw.base.SecureValueType", native_names: Optional[bool] = None, selfie_required: Optional[bool] = None, translation_required: Optional[bool] = None) -> None:
        self.type = type  # SecureValueType
        self.native_names = native_names  # flags.0?true
        self.selfie_required = selfie_required  # flags.1?true
        self.translation_required = translation_required  # flags.2?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        native_names = True if flags & (1 << 0) else False
        selfie_required = True if flags & (1 << 1) else False
        translation_required = True if flags & (1 << 2) else False
        type = TLObject.read(data)
        
        return SecureRequiredType(type=type, native_names=native_names, selfie_required=selfie_required, translation_required=translation_required)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.native_names else 0
        flags |= (1 << 1) if self.selfie_required else 0
        flags |= (1 << 2) if self.translation_required else 0
        data.write(Int(flags))
        
        data.write(self.type.write())
        
        return data.getvalue()
