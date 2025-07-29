from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SecureValueErrorData(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureValueError`.

    Details:
        - Layer: ``135``
        - ID: ``-0x175bf427``

    Parameters:
        type: :obj:`SecureValueType <pyeitaa.raw.base.SecureValueType>`
        data_hash: ``bytes``
        field: ``str``
        text: ``str``
    """

    __slots__: List[str] = ["type", "data_hash", "field", "text"]

    ID = -0x175bf427
    QUALNAME = "types.SecureValueErrorData"

    def __init__(self, *, type: "raw.base.SecureValueType", data_hash: bytes, field: str, text: str) -> None:
        self.type = type  # SecureValueType
        self.data_hash = data_hash  # bytes
        self.field = field  # string
        self.text = text  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = TLObject.read(data)
        
        data_hash = Bytes.read(data)
        
        field = String.read(data)
        
        text = String.read(data)
        
        return SecureValueErrorData(type=type, data_hash=data_hash, field=field, text=text)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.type.write())
        
        data.write(Bytes(self.data_hash))
        
        data.write(String(self.field))
        
        data.write(String(self.text))
        
        return data.getvalue()
