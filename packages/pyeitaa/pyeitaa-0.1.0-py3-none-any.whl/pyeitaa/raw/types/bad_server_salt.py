from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class BadServerSalt(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.BadMsgNotification`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1254bb85``

    Parameters:
        bad_msg_id: ``int`` ``64-bit``
        bad_msg_seqno: ``int`` ``32-bit``
        error_code: ``int`` ``32-bit``
        new_server_salt: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["bad_msg_id", "bad_msg_seqno", "error_code", "new_server_salt"]

    ID = -0x1254bb85
    QUALNAME = "types.BadServerSalt"

    def __init__(self, *, bad_msg_id: int, bad_msg_seqno: int, error_code: int, new_server_salt: int) -> None:
        self.bad_msg_id = bad_msg_id  # long
        self.bad_msg_seqno = bad_msg_seqno  # int
        self.error_code = error_code  # int
        self.new_server_salt = new_server_salt  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        bad_msg_id = Long.read(data)
        
        bad_msg_seqno = Int.read(data)
        
        error_code = Int.read(data)
        
        new_server_salt = Long.read(data)
        
        return BadServerSalt(bad_msg_id=bad_msg_id, bad_msg_seqno=bad_msg_seqno, error_code=error_code, new_server_salt=new_server_salt)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.bad_msg_id))
        
        data.write(Int(self.bad_msg_seqno))
        
        data.write(Int(self.error_code))
        
        data.write(Long(self.new_server_salt))
        
        return data.getvalue()
