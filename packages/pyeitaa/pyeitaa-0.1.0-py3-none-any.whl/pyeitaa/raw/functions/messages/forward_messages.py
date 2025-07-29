from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ForwardMessages(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x260119f2``

    Parameters:
        from_peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        id: List of ``int`` ``32-bit``
        random_id: List of ``int`` ``64-bit``
        to_peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        silent (optional): ``bool``
        background (optional): ``bool``
        with_my_score (optional): ``bool``
        drop_author (optional): ``bool``
        drop_media_captions (optional): ``bool``
        schedule_date (optional): ``int`` ``32-bit``
        noforwards (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["from_peer", "id", "random_id", "to_peer", "silent", "background", "with_my_score", "drop_author", "drop_media_captions", "schedule_date", "noforwards"]

    ID = -0x260119f2
    QUALNAME = "functions.messages.ForwardMessages"

    def __init__(self, *, from_peer: "raw.base.InputPeer", id: List[int], random_id: List[int], to_peer: "raw.base.InputPeer", silent: Optional[bool] = None, background: Optional[bool] = None, with_my_score: Optional[bool] = None, drop_author: Optional[bool] = None, drop_media_captions: Optional[bool] = None, schedule_date: Optional[int] = None, noforwards: Optional[bool] = None) -> None:
        self.from_peer = from_peer  # InputPeer
        self.id = id  # Vector<int>
        self.random_id = random_id  # Vector<long>
        self.to_peer = to_peer  # InputPeer
        self.silent = silent  # flags.5?true
        self.background = background  # flags.6?true
        self.with_my_score = with_my_score  # flags.8?true
        self.drop_author = drop_author  # flags.11?true
        self.drop_media_captions = drop_media_captions  # flags.12?true
        self.schedule_date = schedule_date  # flags.10?int
        self.noforwards = noforwards  # flags.14?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        silent = True if flags & (1 << 5) else False
        background = True if flags & (1 << 6) else False
        with_my_score = True if flags & (1 << 8) else False
        drop_author = True if flags & (1 << 11) else False
        drop_media_captions = True if flags & (1 << 12) else False
        from_peer = TLObject.read(data)
        
        id = TLObject.read(data, Int)
        
        random_id = TLObject.read(data, Long)
        
        to_peer = TLObject.read(data)
        
        schedule_date = Int.read(data) if flags & (1 << 10) else None
        noforwards = True if flags & (1 << 14) else False
        return ForwardMessages(from_peer=from_peer, id=id, random_id=random_id, to_peer=to_peer, silent=silent, background=background, with_my_score=with_my_score, drop_author=drop_author, drop_media_captions=drop_media_captions, schedule_date=schedule_date, noforwards=noforwards)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 5) if self.silent else 0
        flags |= (1 << 6) if self.background else 0
        flags |= (1 << 8) if self.with_my_score else 0
        flags |= (1 << 11) if self.drop_author else 0
        flags |= (1 << 12) if self.drop_media_captions else 0
        flags |= (1 << 10) if self.schedule_date is not None else 0
        flags |= (1 << 14) if self.noforwards else 0
        data.write(Int(flags))
        
        data.write(self.from_peer.write())
        
        data.write(Vector(self.id, Int))
        
        data.write(Vector(self.random_id, Long))
        
        data.write(self.to_peer.write())
        
        if self.schedule_date is not None:
            data.write(Int(self.schedule_date))
        
        return data.getvalue()
