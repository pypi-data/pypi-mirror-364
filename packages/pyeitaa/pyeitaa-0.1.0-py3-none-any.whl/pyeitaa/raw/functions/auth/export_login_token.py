from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ExportLoginToken(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x481f7a02``

    Parameters:
        api_id: ``int`` ``32-bit``
        api_hash: ``str``
        except_ids: List of ``int`` ``64-bit``

    Returns:
        :obj:`auth.LoginToken <pyeitaa.raw.base.auth.LoginToken>`
    """

    __slots__: List[str] = ["api_id", "api_hash", "except_ids"]

    ID = -0x481f7a02
    QUALNAME = "functions.auth.ExportLoginToken"

    def __init__(self, *, api_id: int, api_hash: str, except_ids: List[int]) -> None:
        self.api_id = api_id  # int
        self.api_hash = api_hash  # string
        self.except_ids = except_ids  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        api_id = Int.read(data)
        
        api_hash = String.read(data)
        
        except_ids = TLObject.read(data, Long)
        
        return ExportLoginToken(api_id=api_id, api_hash=api_hash, except_ids=except_ids)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.api_id))
        
        data.write(String(self.api_hash))
        
        data.write(Vector(self.except_ids, Long))
        
        return data.getvalue()
