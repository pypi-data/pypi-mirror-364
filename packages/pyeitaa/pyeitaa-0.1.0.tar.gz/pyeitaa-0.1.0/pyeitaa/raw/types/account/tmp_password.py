from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class TmpPassword(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.TmpPassword`.

    Details:
        - Layer: ``135``
        - ID: ``-0x249b02cc``

    Parameters:
        tmp_password: ``bytes``
        valid_until: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetTmpPassword <pyeitaa.raw.functions.account.GetTmpPassword>`
    """

    __slots__: List[str] = ["tmp_password", "valid_until"]

    ID = -0x249b02cc
    QUALNAME = "types.account.TmpPassword"

    def __init__(self, *, tmp_password: bytes, valid_until: int) -> None:
        self.tmp_password = tmp_password  # bytes
        self.valid_until = valid_until  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        tmp_password = Bytes.read(data)
        
        valid_until = Int.read(data)
        
        return TmpPassword(tmp_password=tmp_password, valid_until=valid_until)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.tmp_password))
        
        data.write(Int(self.valid_until))
        
        return data.getvalue()
