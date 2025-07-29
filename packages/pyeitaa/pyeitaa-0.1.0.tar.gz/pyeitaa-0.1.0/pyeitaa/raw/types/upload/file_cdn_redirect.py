from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class FileCdnRedirect(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.upload.File`.

    Details:
        - Layer: ``135``
        - ID: ``-0xe7325bc``

    Parameters:
        dc_id: ``int`` ``32-bit``
        file_token: ``bytes``
        encryption_key: ``bytes``
        encryption_iv: ``bytes``
        file_hashes: List of :obj:`FileHash <pyeitaa.raw.base.FileHash>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`upload.GetFile <pyeitaa.raw.functions.upload.GetFile>`
            - :obj:`upload.GetFile2 <pyeitaa.raw.functions.upload.GetFile2>`
    """

    __slots__: List[str] = ["dc_id", "file_token", "encryption_key", "encryption_iv", "file_hashes"]

    ID = -0xe7325bc
    QUALNAME = "types.upload.FileCdnRedirect"

    def __init__(self, *, dc_id: int, file_token: bytes, encryption_key: bytes, encryption_iv: bytes, file_hashes: List["raw.base.FileHash"]) -> None:
        self.dc_id = dc_id  # int
        self.file_token = file_token  # bytes
        self.encryption_key = encryption_key  # bytes
        self.encryption_iv = encryption_iv  # bytes
        self.file_hashes = file_hashes  # Vector<FileHash>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        dc_id = Int.read(data)
        
        file_token = Bytes.read(data)
        
        encryption_key = Bytes.read(data)
        
        encryption_iv = Bytes.read(data)
        
        file_hashes = TLObject.read(data)
        
        return FileCdnRedirect(dc_id=dc_id, file_token=file_token, encryption_key=encryption_key, encryption_iv=encryption_iv, file_hashes=file_hashes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.dc_id))
        
        data.write(Bytes(self.file_token))
        
        data.write(Bytes(self.encryption_key))
        
        data.write(Bytes(self.encryption_iv))
        
        data.write(Vector(self.file_hashes))
        
        return data.getvalue()
