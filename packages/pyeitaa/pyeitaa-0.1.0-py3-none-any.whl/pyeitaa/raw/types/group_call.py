from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class GroupCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.GroupCall`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2a689af4``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        participants_count: ``int`` ``32-bit``
        unmuted_video_limit: ``int`` ``32-bit``
        version: ``int`` ``32-bit``
        join_muted (optional): ``bool``
        can_change_join_muted (optional): ``bool``
        join_date_asc (optional): ``bool``
        schedule_start_subscribed (optional): ``bool``
        can_start_video (optional): ``bool``
        record_video_active (optional): ``bool``
        title (optional): ``str``
        stream_dc_id (optional): ``int`` ``32-bit``
        record_start_date (optional): ``int`` ``32-bit``
        schedule_date (optional): ``int`` ``32-bit``
        unmuted_video_count (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "access_hash", "participants_count", "unmuted_video_limit", "version", "join_muted", "can_change_join_muted", "join_date_asc", "schedule_start_subscribed", "can_start_video", "record_video_active", "title", "stream_dc_id", "record_start_date", "schedule_date", "unmuted_video_count"]

    ID = -0x2a689af4
    QUALNAME = "types.GroupCall"

    def __init__(self, *, id: int, access_hash: int, participants_count: int, unmuted_video_limit: int, version: int, join_muted: Optional[bool] = None, can_change_join_muted: Optional[bool] = None, join_date_asc: Optional[bool] = None, schedule_start_subscribed: Optional[bool] = None, can_start_video: Optional[bool] = None, record_video_active: Optional[bool] = None, title: Optional[str] = None, stream_dc_id: Optional[int] = None, record_start_date: Optional[int] = None, schedule_date: Optional[int] = None, unmuted_video_count: Optional[int] = None) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.participants_count = participants_count  # int
        self.unmuted_video_limit = unmuted_video_limit  # int
        self.version = version  # int
        self.join_muted = join_muted  # flags.1?true
        self.can_change_join_muted = can_change_join_muted  # flags.2?true
        self.join_date_asc = join_date_asc  # flags.6?true
        self.schedule_start_subscribed = schedule_start_subscribed  # flags.8?true
        self.can_start_video = can_start_video  # flags.9?true
        self.record_video_active = record_video_active  # flags.11?true
        self.title = title  # flags.3?string
        self.stream_dc_id = stream_dc_id  # flags.4?int
        self.record_start_date = record_start_date  # flags.5?int
        self.schedule_date = schedule_date  # flags.7?int
        self.unmuted_video_count = unmuted_video_count  # flags.10?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        join_muted = True if flags & (1 << 1) else False
        can_change_join_muted = True if flags & (1 << 2) else False
        join_date_asc = True if flags & (1 << 6) else False
        schedule_start_subscribed = True if flags & (1 << 8) else False
        can_start_video = True if flags & (1 << 9) else False
        record_video_active = True if flags & (1 << 11) else False
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        participants_count = Int.read(data)
        
        title = String.read(data) if flags & (1 << 3) else None
        stream_dc_id = Int.read(data) if flags & (1 << 4) else None
        record_start_date = Int.read(data) if flags & (1 << 5) else None
        schedule_date = Int.read(data) if flags & (1 << 7) else None
        unmuted_video_count = Int.read(data) if flags & (1 << 10) else None
        unmuted_video_limit = Int.read(data)
        
        version = Int.read(data)
        
        return GroupCall(id=id, access_hash=access_hash, participants_count=participants_count, unmuted_video_limit=unmuted_video_limit, version=version, join_muted=join_muted, can_change_join_muted=can_change_join_muted, join_date_asc=join_date_asc, schedule_start_subscribed=schedule_start_subscribed, can_start_video=can_start_video, record_video_active=record_video_active, title=title, stream_dc_id=stream_dc_id, record_start_date=record_start_date, schedule_date=schedule_date, unmuted_video_count=unmuted_video_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.join_muted else 0
        flags |= (1 << 2) if self.can_change_join_muted else 0
        flags |= (1 << 6) if self.join_date_asc else 0
        flags |= (1 << 8) if self.schedule_start_subscribed else 0
        flags |= (1 << 9) if self.can_start_video else 0
        flags |= (1 << 11) if self.record_video_active else 0
        flags |= (1 << 3) if self.title is not None else 0
        flags |= (1 << 4) if self.stream_dc_id is not None else 0
        flags |= (1 << 5) if self.record_start_date is not None else 0
        flags |= (1 << 7) if self.schedule_date is not None else 0
        flags |= (1 << 10) if self.unmuted_video_count is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.participants_count))
        
        if self.title is not None:
            data.write(String(self.title))
        
        if self.stream_dc_id is not None:
            data.write(Int(self.stream_dc_id))
        
        if self.record_start_date is not None:
            data.write(Int(self.record_start_date))
        
        if self.schedule_date is not None:
            data.write(Int(self.schedule_date))
        
        if self.unmuted_video_count is not None:
            data.write(Int(self.unmuted_video_count))
        
        data.write(Int(self.unmuted_video_limit))
        
        data.write(Int(self.version))
        
        return data.getvalue()
