from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ChannelAdminLogEventsFilter(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventsFilter`.

    Details:
        - Layer: ``135``
        - ID: ``-0x15ef851c``

    Parameters:
        join (optional): ``bool``
        leave (optional): ``bool``
        invite (optional): ``bool``
        ban (optional): ``bool``
        unban (optional): ``bool``
        kick (optional): ``bool``
        unkick (optional): ``bool``
        promote (optional): ``bool``
        demote (optional): ``bool``
        info (optional): ``bool``
        settings (optional): ``bool``
        pinned (optional): ``bool``
        edit (optional): ``bool``
        delete (optional): ``bool``
        group_call (optional): ``bool``
        invites (optional): ``bool``
    """

    __slots__: List[str] = ["join", "leave", "invite", "ban", "unban", "kick", "unkick", "promote", "demote", "info", "settings", "pinned", "edit", "delete", "group_call", "invites"]

    ID = -0x15ef851c
    QUALNAME = "types.ChannelAdminLogEventsFilter"

    def __init__(self, *, join: Optional[bool] = None, leave: Optional[bool] = None, invite: Optional[bool] = None, ban: Optional[bool] = None, unban: Optional[bool] = None, kick: Optional[bool] = None, unkick: Optional[bool] = None, promote: Optional[bool] = None, demote: Optional[bool] = None, info: Optional[bool] = None, settings: Optional[bool] = None, pinned: Optional[bool] = None, edit: Optional[bool] = None, delete: Optional[bool] = None, group_call: Optional[bool] = None, invites: Optional[bool] = None) -> None:
        self.join = join  # flags.0?true
        self.leave = leave  # flags.1?true
        self.invite = invite  # flags.2?true
        self.ban = ban  # flags.3?true
        self.unban = unban  # flags.4?true
        self.kick = kick  # flags.5?true
        self.unkick = unkick  # flags.6?true
        self.promote = promote  # flags.7?true
        self.demote = demote  # flags.8?true
        self.info = info  # flags.9?true
        self.settings = settings  # flags.10?true
        self.pinned = pinned  # flags.11?true
        self.edit = edit  # flags.12?true
        self.delete = delete  # flags.13?true
        self.group_call = group_call  # flags.14?true
        self.invites = invites  # flags.15?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        join = True if flags & (1 << 0) else False
        leave = True if flags & (1 << 1) else False
        invite = True if flags & (1 << 2) else False
        ban = True if flags & (1 << 3) else False
        unban = True if flags & (1 << 4) else False
        kick = True if flags & (1 << 5) else False
        unkick = True if flags & (1 << 6) else False
        promote = True if flags & (1 << 7) else False
        demote = True if flags & (1 << 8) else False
        info = True if flags & (1 << 9) else False
        settings = True if flags & (1 << 10) else False
        pinned = True if flags & (1 << 11) else False
        edit = True if flags & (1 << 12) else False
        delete = True if flags & (1 << 13) else False
        group_call = True if flags & (1 << 14) else False
        invites = True if flags & (1 << 15) else False
        return ChannelAdminLogEventsFilter(join=join, leave=leave, invite=invite, ban=ban, unban=unban, kick=kick, unkick=unkick, promote=promote, demote=demote, info=info, settings=settings, pinned=pinned, edit=edit, delete=delete, group_call=group_call, invites=invites)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.join else 0
        flags |= (1 << 1) if self.leave else 0
        flags |= (1 << 2) if self.invite else 0
        flags |= (1 << 3) if self.ban else 0
        flags |= (1 << 4) if self.unban else 0
        flags |= (1 << 5) if self.kick else 0
        flags |= (1 << 6) if self.unkick else 0
        flags |= (1 << 7) if self.promote else 0
        flags |= (1 << 8) if self.demote else 0
        flags |= (1 << 9) if self.info else 0
        flags |= (1 << 10) if self.settings else 0
        flags |= (1 << 11) if self.pinned else 0
        flags |= (1 << 12) if self.edit else 0
        flags |= (1 << 13) if self.delete else 0
        flags |= (1 << 14) if self.group_call else 0
        flags |= (1 << 15) if self.invites else 0
        data.write(Int(flags))
        
        return data.getvalue()
