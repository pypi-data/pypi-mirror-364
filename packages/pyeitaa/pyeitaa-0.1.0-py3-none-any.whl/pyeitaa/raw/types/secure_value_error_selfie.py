from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SecureValueErrorSelfie(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureValueError`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1ac8312a``

    Parameters:
        type: :obj:`SecureValueType <pyeitaa.raw.base.SecureValueType>`
        file_hash: ``bytes``
        text: ``str``
    """

    __slots__: List[str] = ["type", "file_hash", "text"]

    ID = -0x1ac8312a
    QUALNAME = "types.SecureValueErrorSelfie"

    def __init__(self, *, type: "raw.base.SecureValueType", file_hash: bytes, text: str) -> None:
        self.type = type  # SecureValueType
        self.file_hash = file_hash  # bytes
        self.text = text  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = TLObject.read(data)
        
        file_hash = Bytes.read(data)
        
        text = String.read(data)
        
        return SecureValueErrorSelfie(type=type, file_hash=file_hash, text=text)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.type.write())
        
        data.write(Bytes(self.file_hash))
        
        data.write(String(self.text))
        
        return data.getvalue()
