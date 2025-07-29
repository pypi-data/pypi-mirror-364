from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SecureValueHash(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureValueHash`.

    Details:
        - Layer: ``135``
        - ID: ``-0x12e13250``

    Parameters:
        type: :obj:`SecureValueType <pyeitaa.raw.base.SecureValueType>`
        hash: ``bytes``
    """

    __slots__: List[str] = ["type", "hash"]

    ID = -0x12e13250
    QUALNAME = "types.SecureValueHash"

    def __init__(self, *, type: "raw.base.SecureValueType", hash: bytes) -> None:
        self.type = type  # SecureValueType
        self.hash = hash  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = TLObject.read(data)
        
        hash = Bytes.read(data)
        
        return SecureValueHash(type=type, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.type.write())
        
        data.write(Bytes(self.hash))
        
        return data.getvalue()
