from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Folder(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Folder`.

    Details:
        - Layer: ``135``
        - ID: ``-0xabb19b``

    Parameters:
        id: ``int`` ``32-bit``
        title: ``str``
        autofill_new_broadcasts (optional): ``bool``
        autofill_public_groups (optional): ``bool``
        autofill_new_correspondents (optional): ``bool``
        photo (optional): :obj:`ChatPhoto <pyeitaa.raw.base.ChatPhoto>`
    """

    __slots__: List[str] = ["id", "title", "autofill_new_broadcasts", "autofill_public_groups", "autofill_new_correspondents", "photo"]

    ID = -0xabb19b
    QUALNAME = "types.Folder"

    def __init__(self, *, id: int, title: str, autofill_new_broadcasts: Optional[bool] = None, autofill_public_groups: Optional[bool] = None, autofill_new_correspondents: Optional[bool] = None, photo: "raw.base.ChatPhoto" = None) -> None:
        self.id = id  # int
        self.title = title  # string
        self.autofill_new_broadcasts = autofill_new_broadcasts  # flags.0?true
        self.autofill_public_groups = autofill_public_groups  # flags.1?true
        self.autofill_new_correspondents = autofill_new_correspondents  # flags.2?true
        self.photo = photo  # flags.3?ChatPhoto

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        autofill_new_broadcasts = True if flags & (1 << 0) else False
        autofill_public_groups = True if flags & (1 << 1) else False
        autofill_new_correspondents = True if flags & (1 << 2) else False
        id = Int.read(data)
        
        title = String.read(data)
        
        photo = TLObject.read(data) if flags & (1 << 3) else None
        
        return Folder(id=id, title=title, autofill_new_broadcasts=autofill_new_broadcasts, autofill_public_groups=autofill_public_groups, autofill_new_correspondents=autofill_new_correspondents, photo=photo)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.autofill_new_broadcasts else 0
        flags |= (1 << 1) if self.autofill_public_groups else 0
        flags |= (1 << 2) if self.autofill_new_correspondents else 0
        flags |= (1 << 3) if self.photo is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.id))
        
        data.write(String(self.title))
        
        if self.photo is not None:
            data.write(self.photo.write())
        
        return data.getvalue()
