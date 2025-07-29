from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class HistoryImportParsed(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.HistoryImportParsed`.

    Details:
        - Layer: ``135``
        - ID: ``0x5e0fb7b9``

    Parameters:
        pm (optional): ``bool``
        group (optional): ``bool``
        title (optional): ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.CheckHistoryImport <pyeitaa.raw.functions.messages.CheckHistoryImport>`
    """

    __slots__: List[str] = ["pm", "group", "title"]

    ID = 0x5e0fb7b9
    QUALNAME = "types.messages.HistoryImportParsed"

    def __init__(self, *, pm: Optional[bool] = None, group: Optional[bool] = None, title: Optional[str] = None) -> None:
        self.pm = pm  # flags.0?true
        self.group = group  # flags.1?true
        self.title = title  # flags.2?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        pm = True if flags & (1 << 0) else False
        group = True if flags & (1 << 1) else False
        title = String.read(data) if flags & (1 << 2) else None
        return HistoryImportParsed(pm=pm, group=group, title=title)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.pm else 0
        flags |= (1 << 1) if self.group else 0
        flags |= (1 << 2) if self.title is not None else 0
        data.write(Int(flags))
        
        if self.title is not None:
            data.write(String(self.title))
        
        return data.getvalue()
