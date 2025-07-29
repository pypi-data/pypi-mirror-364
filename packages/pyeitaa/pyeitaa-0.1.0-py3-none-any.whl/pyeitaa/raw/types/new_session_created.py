from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class NewSessionCreated(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.NewSession`.

    Details:
        - Layer: ``135``
        - ID: ``-0x613df6f8``

    Parameters:
        first_msg_id: ``int`` ``64-bit``
        unique_id: ``int`` ``64-bit``
        server_salt: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["first_msg_id", "unique_id", "server_salt"]

    ID = -0x613df6f8
    QUALNAME = "types.NewSessionCreated"

    def __init__(self, *, first_msg_id: int, unique_id: int, server_salt: int) -> None:
        self.first_msg_id = first_msg_id  # long
        self.unique_id = unique_id  # long
        self.server_salt = server_salt  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        first_msg_id = Long.read(data)
        
        unique_id = Long.read(data)
        
        server_salt = Long.read(data)
        
        return NewSessionCreated(first_msg_id=first_msg_id, unique_id=unique_id, server_salt=server_salt)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.first_msg_id))
        
        data.write(Long(self.unique_id))
        
        data.write(Long(self.server_salt))
        
        return data.getvalue()
