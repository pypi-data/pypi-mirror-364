from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SecureValueErrorTranslationFiles(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureValueError`.

    Details:
        - Layer: ``135``
        - ID: ``0x34636dd8``

    Parameters:
        type: :obj:`SecureValueType <pyeitaa.raw.base.SecureValueType>`
        file_hash: List of ``bytes``
        text: ``str``
    """

    __slots__: List[str] = ["type", "file_hash", "text"]

    ID = 0x34636dd8
    QUALNAME = "types.SecureValueErrorTranslationFiles"

    def __init__(self, *, type: "raw.base.SecureValueType", file_hash: List[bytes], text: str) -> None:
        self.type = type  # SecureValueType
        self.file_hash = file_hash  # Vector<bytes>
        self.text = text  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = TLObject.read(data)
        
        file_hash = TLObject.read(data, Bytes)
        
        text = String.read(data)
        
        return SecureValueErrorTranslationFiles(type=type, file_hash=file_hash, text=text)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.type.write())
        
        data.write(Vector(self.file_hash, Bytes))
        
        data.write(String(self.text))
        
        return data.getvalue()
