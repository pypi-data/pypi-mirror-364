from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class BlockFromReplies(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x29a8962c``

    Parameters:
        msg_id: ``int`` ``32-bit``
        delete_message (optional): ``bool``
        delete_history (optional): ``bool``
        report_spam (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["msg_id", "delete_message", "delete_history", "report_spam"]

    ID = 0x29a8962c
    QUALNAME = "functions.contacts.BlockFromReplies"

    def __init__(self, *, msg_id: int, delete_message: Optional[bool] = None, delete_history: Optional[bool] = None, report_spam: Optional[bool] = None) -> None:
        self.msg_id = msg_id  # int
        self.delete_message = delete_message  # flags.0?true
        self.delete_history = delete_history  # flags.1?true
        self.report_spam = report_spam  # flags.2?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        delete_message = True if flags & (1 << 0) else False
        delete_history = True if flags & (1 << 1) else False
        report_spam = True if flags & (1 << 2) else False
        msg_id = Int.read(data)
        
        return BlockFromReplies(msg_id=msg_id, delete_message=delete_message, delete_history=delete_history, report_spam=report_spam)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.delete_message else 0
        flags |= (1 << 1) if self.delete_history else 0
        flags |= (1 << 2) if self.report_spam else 0
        data.write(Int(flags))
        
        data.write(Int(self.msg_id))
        
        return data.getvalue()
