from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class DeepLinkInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.DeepLinkInfo`.

    Details:
        - Layer: ``135``
        - ID: ``0x6a4ee832``

    Parameters:
        message: ``str``
        update_app (optional): ``bool``
        entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetDeepLinkInfo <pyeitaa.raw.functions.help.GetDeepLinkInfo>`
    """

    __slots__: List[str] = ["message", "update_app", "entities"]

    ID = 0x6a4ee832
    QUALNAME = "types.help.DeepLinkInfo"

    def __init__(self, *, message: str, update_app: Optional[bool] = None, entities: Optional[List["raw.base.MessageEntity"]] = None) -> None:
        self.message = message  # string
        self.update_app = update_app  # flags.0?true
        self.entities = entities  # flags.1?Vector<MessageEntity>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        update_app = True if flags & (1 << 0) else False
        message = String.read(data)
        
        entities = TLObject.read(data) if flags & (1 << 1) else []
        
        return DeepLinkInfo(message=message, update_app=update_app, entities=entities)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.update_app else 0
        flags |= (1 << 1) if self.entities is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.message))
        
        if self.entities is not None:
            data.write(Vector(self.entities))
        
        return data.getvalue()
