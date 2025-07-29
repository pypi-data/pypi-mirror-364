from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SecureValue(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureValue`.

    Details:
        - Layer: ``135``
        - ID: ``0x187fa0ca``

    Parameters:
        type: :obj:`SecureValueType <pyeitaa.raw.base.SecureValueType>`
        hash: ``bytes``
        data (optional): :obj:`SecureData <pyeitaa.raw.base.SecureData>`
        front_side (optional): :obj:`SecureFile <pyeitaa.raw.base.SecureFile>`
        reverse_side (optional): :obj:`SecureFile <pyeitaa.raw.base.SecureFile>`
        selfie (optional): :obj:`SecureFile <pyeitaa.raw.base.SecureFile>`
        translation (optional): List of :obj:`SecureFile <pyeitaa.raw.base.SecureFile>`
        files (optional): List of :obj:`SecureFile <pyeitaa.raw.base.SecureFile>`
        plain_data (optional): :obj:`SecurePlainData <pyeitaa.raw.base.SecurePlainData>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAllSecureValues <pyeitaa.raw.functions.account.GetAllSecureValues>`
            - :obj:`account.GetSecureValue <pyeitaa.raw.functions.account.GetSecureValue>`
            - :obj:`account.SaveSecureValue <pyeitaa.raw.functions.account.SaveSecureValue>`
    """

    __slots__: List[str] = ["type", "hash", "data", "front_side", "reverse_side", "selfie", "translation", "files", "plain_data"]

    ID = 0x187fa0ca
    QUALNAME = "types.SecureValue"

    def __init__(self, *, type: "raw.base.SecureValueType", hash: bytes, data: "raw.base.SecureData" = None, front_side: "raw.base.SecureFile" = None, reverse_side: "raw.base.SecureFile" = None, selfie: "raw.base.SecureFile" = None, translation: Optional[List["raw.base.SecureFile"]] = None, files: Optional[List["raw.base.SecureFile"]] = None, plain_data: "raw.base.SecurePlainData" = None) -> None:
        self.type = type  # SecureValueType
        self.hash = hash  # bytes
        self.data = data  # flags.0?SecureData
        self.front_side = front_side  # flags.1?SecureFile
        self.reverse_side = reverse_side  # flags.2?SecureFile
        self.selfie = selfie  # flags.3?SecureFile
        self.translation = translation  # flags.6?Vector<SecureFile>
        self.files = files  # flags.4?Vector<SecureFile>
        self.plain_data = plain_data  # flags.5?SecurePlainData

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        type = TLObject.read(data)
        
        data = TLObject.read(data) if flags & (1 << 0) else None
        
        front_side = TLObject.read(data) if flags & (1 << 1) else None
        
        reverse_side = TLObject.read(data) if flags & (1 << 2) else None
        
        selfie = TLObject.read(data) if flags & (1 << 3) else None
        
        translation = TLObject.read(data) if flags & (1 << 6) else []
        
        files = TLObject.read(data) if flags & (1 << 4) else []
        
        plain_data = TLObject.read(data) if flags & (1 << 5) else None
        
        hash = Bytes.read(data)
        
        return SecureValue(type=type, hash=hash, data=data, front_side=front_side, reverse_side=reverse_side, selfie=selfie, translation=translation, files=files, plain_data=plain_data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.data is not None else 0
        flags |= (1 << 1) if self.front_side is not None else 0
        flags |= (1 << 2) if self.reverse_side is not None else 0
        flags |= (1 << 3) if self.selfie is not None else 0
        flags |= (1 << 6) if self.translation is not None else 0
        flags |= (1 << 4) if self.files is not None else 0
        flags |= (1 << 5) if self.plain_data is not None else 0
        data.write(Int(flags))
        
        data.write(self.type.write())
        
        if self.data is not None:
            data.write(self.data.write())
        
        if self.front_side is not None:
            data.write(self.front_side.write())
        
        if self.reverse_side is not None:
            data.write(self.reverse_side.write())
        
        if self.selfie is not None:
            data.write(self.selfie.write())
        
        if self.translation is not None:
            data.write(Vector(self.translation))
        
        if self.files is not None:
            data.write(Vector(self.files))
        
        if self.plain_data is not None:
            data.write(self.plain_data.write())
        
        data.write(Bytes(self.hash))
        
        return data.getvalue()
