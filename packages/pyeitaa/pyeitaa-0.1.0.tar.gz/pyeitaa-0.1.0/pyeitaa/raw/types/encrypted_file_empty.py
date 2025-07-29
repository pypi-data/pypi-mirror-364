from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EncryptedFileEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EncryptedFile`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3de0b682``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.UploadEncryptedFile <pyeitaa.raw.functions.messages.UploadEncryptedFile>`
    """

    __slots__: List[str] = []

    ID = -0x3de0b682
    QUALNAME = "types.EncryptedFileEmpty"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return EncryptedFileEmpty()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
