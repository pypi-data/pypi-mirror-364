from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class InputMessagesFilterPhoneCalls(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessagesFilter`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7f366898``

    Parameters:
        missed (optional): ``bool``
    """

    __slots__: List[str] = ["missed"]

    ID = -0x7f366898
    QUALNAME = "types.InputMessagesFilterPhoneCalls"

    def __init__(self, *, missed: Optional[bool] = None) -> None:
        self.missed = missed  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        missed = True if flags & (1 << 0) else False
        return InputMessagesFilterPhoneCalls(missed=missed)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.missed else 0
        data.write(Int(flags))
        
        return data.getvalue()
