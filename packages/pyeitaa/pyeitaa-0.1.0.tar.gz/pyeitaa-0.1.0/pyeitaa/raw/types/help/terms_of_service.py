from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class TermsOfService(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.TermsOfService`.

    Details:
        - Layer: ``135``
        - ID: ``0x780a0310``

    Parameters:
        id: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
        text: ``str``
        entities: List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
        popup (optional): ``bool``
        min_age_confirm (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "text", "entities", "popup", "min_age_confirm"]

    ID = 0x780a0310
    QUALNAME = "types.help.TermsOfService"

    def __init__(self, *, id: "raw.base.DataJSON", text: str, entities: List["raw.base.MessageEntity"], popup: Optional[bool] = None, min_age_confirm: Optional[int] = None) -> None:
        self.id = id  # DataJSON
        self.text = text  # string
        self.entities = entities  # Vector<MessageEntity>
        self.popup = popup  # flags.0?true
        self.min_age_confirm = min_age_confirm  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        popup = True if flags & (1 << 0) else False
        id = TLObject.read(data)
        
        text = String.read(data)
        
        entities = TLObject.read(data)
        
        min_age_confirm = Int.read(data) if flags & (1 << 1) else None
        return TermsOfService(id=id, text=text, entities=entities, popup=popup, min_age_confirm=min_age_confirm)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.popup else 0
        flags |= (1 << 1) if self.min_age_confirm is not None else 0
        data.write(Int(flags))
        
        data.write(self.id.write())
        
        data.write(String(self.text))
        
        data.write(Vector(self.entities))
        
        if self.min_age_confirm is not None:
            data.write(Int(self.min_age_confirm))
        
        return data.getvalue()
