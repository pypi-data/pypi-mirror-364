from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SponsoredMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SponsoredMessage`.

    Details:
        - Layer: ``135``
        - ID: ``0x2a3c381f``

    Parameters:
        random_id: ``bytes``
        from_id: :obj:`Peer <pyeitaa.raw.base.Peer>`
        message: ``str``
        start_param (optional): ``str``
        entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
    """

    __slots__: List[str] = ["random_id", "from_id", "message", "start_param", "entities"]

    ID = 0x2a3c381f
    QUALNAME = "types.SponsoredMessage"

    def __init__(self, *, random_id: bytes, from_id: "raw.base.Peer", message: str, start_param: Optional[str] = None, entities: Optional[List["raw.base.MessageEntity"]] = None) -> None:
        self.random_id = random_id  # bytes
        self.from_id = from_id  # Peer
        self.message = message  # string
        self.start_param = start_param  # flags.0?string
        self.entities = entities  # flags.1?Vector<MessageEntity>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        random_id = Bytes.read(data)
        
        from_id = TLObject.read(data)
        
        start_param = String.read(data) if flags & (1 << 0) else None
        message = String.read(data)
        
        entities = TLObject.read(data) if flags & (1 << 1) else []
        
        return SponsoredMessage(random_id=random_id, from_id=from_id, message=message, start_param=start_param, entities=entities)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.start_param is not None else 0
        flags |= (1 << 1) if self.entities is not None else 0
        data.write(Int(flags))
        
        data.write(Bytes(self.random_id))
        
        data.write(self.from_id.write())
        
        if self.start_param is not None:
            data.write(String(self.start_param))
        
        data.write(String(self.message))
        
        if self.entities is not None:
            data.write(Vector(self.entities))
        
        return data.getvalue()
