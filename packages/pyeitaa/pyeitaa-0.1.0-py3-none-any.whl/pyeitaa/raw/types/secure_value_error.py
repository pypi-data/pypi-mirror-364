from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SecureValueError(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureValueError`.

    Details:
        - Layer: ``135``
        - ID: ``-0x79628a71``

    Parameters:
        type: :obj:`SecureValueType <pyeitaa.raw.base.SecureValueType>`
        hash: ``bytes``
        text: ``str``
    """

    __slots__: List[str] = ["type", "hash", "text"]

    ID = -0x79628a71
    QUALNAME = "types.SecureValueError"

    def __init__(self, *, type: "raw.base.SecureValueType", hash: bytes, text: str) -> None:
        self.type = type  # SecureValueType
        self.hash = hash  # bytes
        self.text = text  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = TLObject.read(data)
        
        hash = Bytes.read(data)
        
        text = String.read(data)
        
        return SecureValueError(type=type, hash=hash, text=text)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.type.write())
        
        data.write(Bytes(self.hash))
        
        data.write(String(self.text))
        
        return data.getvalue()
