from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ContentSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.ContentSettings`.

    Details:
        - Layer: ``135``
        - ID: ``0x57e28221``

    Parameters:
        sensitive_enabled (optional): ``bool``
        sensitive_can_change (optional): ``bool``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetContentSettings <pyeitaa.raw.functions.account.GetContentSettings>`
    """

    __slots__: List[str] = ["sensitive_enabled", "sensitive_can_change"]

    ID = 0x57e28221
    QUALNAME = "types.account.ContentSettings"

    def __init__(self, *, sensitive_enabled: Optional[bool] = None, sensitive_can_change: Optional[bool] = None) -> None:
        self.sensitive_enabled = sensitive_enabled  # flags.0?true
        self.sensitive_can_change = sensitive_can_change  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        sensitive_enabled = True if flags & (1 << 0) else False
        sensitive_can_change = True if flags & (1 << 1) else False
        return ContentSettings(sensitive_enabled=sensitive_enabled, sensitive_can_change=sensitive_can_change)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.sensitive_enabled else 0
        flags |= (1 << 1) if self.sensitive_can_change else 0
        data.write(Int(flags))
        
        return data.getvalue()
