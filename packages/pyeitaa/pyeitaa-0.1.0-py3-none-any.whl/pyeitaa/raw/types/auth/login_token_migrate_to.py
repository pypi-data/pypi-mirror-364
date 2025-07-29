from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class LoginTokenMigrateTo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.LoginToken`.

    Details:
        - Layer: ``135``
        - ID: ``0x68e9916``

    Parameters:
        dc_id: ``int`` ``32-bit``
        token: ``bytes``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`auth.ExportLoginToken <pyeitaa.raw.functions.auth.ExportLoginToken>`
            - :obj:`auth.ImportLoginToken <pyeitaa.raw.functions.auth.ImportLoginToken>`
    """

    __slots__: List[str] = ["dc_id", "token"]

    ID = 0x68e9916
    QUALNAME = "types.auth.LoginTokenMigrateTo"

    def __init__(self, *, dc_id: int, token: bytes) -> None:
        self.dc_id = dc_id  # int
        self.token = token  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        dc_id = Int.read(data)
        
        token = Bytes.read(data)
        
        return LoginTokenMigrateTo(dc_id=dc_id, token=token)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.dc_id))
        
        data.write(Bytes(self.token))
        
        return data.getvalue()
