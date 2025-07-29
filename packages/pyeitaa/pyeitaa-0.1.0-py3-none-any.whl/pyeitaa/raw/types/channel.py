from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Channel(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Chat`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7d9e539f``

    Parameters:
        id: ``int`` ``64-bit``
        title: ``str``
        photo: :obj:`ChatPhoto <pyeitaa.raw.base.ChatPhoto>`
        date: ``int`` ``32-bit``
        creator (optional): ``bool``
        left (optional): ``bool``
        broadcast (optional): ``bool``
        verified (optional): ``bool``
        megagroup (optional): ``bool``
        restricted (optional): ``bool``
        signatures (optional): ``bool``
        min (optional): ``bool``
        scam (optional): ``bool``
        has_link (optional): ``bool``
        has_geo (optional): ``bool``
        slowmode_enabled (optional): ``bool``
        call_active (optional): ``bool``
        call_not_empty (optional): ``bool``
        fake (optional): ``bool``
        gigagroup (optional): ``bool``
        noforwards (optional): ``bool``
        access_hash (optional): ``int`` ``64-bit``
        username (optional): ``str``
        restriction_reason (optional): List of :obj:`RestrictionReason <pyeitaa.raw.base.RestrictionReason>`
        admin_rights (optional): :obj:`ChatAdminRights <pyeitaa.raw.base.ChatAdminRights>`
        banned_rights (optional): :obj:`ChatBannedRights <pyeitaa.raw.base.ChatBannedRights>`
        default_banned_rights (optional): :obj:`ChatBannedRights <pyeitaa.raw.base.ChatBannedRights>`
        participants_count (optional): ``int`` ``32-bit``
        live_msg_id (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "title", "photo", "date", "creator", "left", "broadcast", "verified", "megagroup", "restricted", "signatures", "min", "scam", "has_link", "has_geo", "slowmode_enabled", "call_active", "call_not_empty", "fake", "gigagroup", "noforwards", "access_hash", "username", "restriction_reason", "admin_rights", "banned_rights", "default_banned_rights", "participants_count", "live_msg_id"]

    ID = -0x7d9e539f
    QUALNAME = "types.Channel"

    def __init__(self, *, id: int, title: str, photo: "raw.base.ChatPhoto", date: int, creator: Optional[bool] = None, left: Optional[bool] = None, broadcast: Optional[bool] = None, verified: Optional[bool] = None, megagroup: Optional[bool] = None, restricted: Optional[bool] = None, signatures: Optional[bool] = None, min: Optional[bool] = None, scam: Optional[bool] = None, has_link: Optional[bool] = None, has_geo: Optional[bool] = None, slowmode_enabled: Optional[bool] = None, call_active: Optional[bool] = None, call_not_empty: Optional[bool] = None, fake: Optional[bool] = None, gigagroup: Optional[bool] = None, noforwards: Optional[bool] = None, access_hash: Optional[int] = None, username: Optional[str] = None, restriction_reason: Optional[List["raw.base.RestrictionReason"]] = None, admin_rights: "raw.base.ChatAdminRights" = None, banned_rights: "raw.base.ChatBannedRights" = None, default_banned_rights: "raw.base.ChatBannedRights" = None, participants_count: Optional[int] = None, live_msg_id: Optional[int] = None) -> None:
        self.id = id  # long
        self.title = title  # string
        self.photo = photo  # ChatPhoto
        self.date = date  # int
        self.creator = creator  # flags.0?true
        self.left = left  # flags.2?true
        self.broadcast = broadcast  # flags.5?true
        self.verified = verified  # flags.7?true
        self.megagroup = megagroup  # flags.8?true
        self.restricted = restricted  # flags.9?true
        self.signatures = signatures  # flags.11?true
        self.min = min  # flags.12?true
        self.scam = scam  # flags.19?true
        self.has_link = has_link  # flags.20?true
        self.has_geo = has_geo  # flags.21?true
        self.slowmode_enabled = slowmode_enabled  # flags.22?true
        self.call_active = call_active  # flags.23?true
        self.call_not_empty = call_not_empty  # flags.24?true
        self.fake = fake  # flags.25?true
        self.gigagroup = gigagroup  # flags.26?true
        self.noforwards = noforwards  # flags.27?true
        self.access_hash = access_hash  # flags.13?long
        self.username = username  # flags.6?string
        self.restriction_reason = restriction_reason  # flags.9?Vector<RestrictionReason>
        self.admin_rights = admin_rights  # flags.14?ChatAdminRights
        self.banned_rights = banned_rights  # flags.15?ChatBannedRights
        self.default_banned_rights = default_banned_rights  # flags.18?ChatBannedRights
        self.participants_count = participants_count  # flags.17?int
        self.live_msg_id = live_msg_id  # flags.29?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        creator = True if flags & (1 << 0) else False
        left = True if flags & (1 << 2) else False
        broadcast = True if flags & (1 << 5) else False
        verified = True if flags & (1 << 7) else False
        megagroup = True if flags & (1 << 8) else False
        restricted = True if flags & (1 << 9) else False
        signatures = True if flags & (1 << 11) else False
        min = True if flags & (1 << 12) else False
        scam = True if flags & (1 << 19) else False
        has_link = True if flags & (1 << 20) else False
        has_geo = True if flags & (1 << 21) else False
        slowmode_enabled = True if flags & (1 << 22) else False
        call_active = True if flags & (1 << 23) else False
        call_not_empty = True if flags & (1 << 24) else False
        fake = True if flags & (1 << 25) else False
        gigagroup = True if flags & (1 << 26) else False
        noforwards = True if flags & (1 << 27) else False
        id = Long.read(data)
        
        access_hash = Long.read(data) if flags & (1 << 13) else None
        title = String.read(data)
        
        username = String.read(data) if flags & (1 << 6) else None
        photo = TLObject.read(data)
        
        date = Int.read(data)
        
        restriction_reason = TLObject.read(data) if flags & (1 << 9) else []
        
        admin_rights = TLObject.read(data) if flags & (1 << 14) else None
        
        banned_rights = TLObject.read(data) if flags & (1 << 15) else None
        
        default_banned_rights = TLObject.read(data) if flags & (1 << 18) else None
        
        participants_count = Int.read(data) if flags & (1 << 17) else None
        live_msg_id = Int.read(data) if flags & (1 << 29) else None
        return Channel(id=id, title=title, photo=photo, date=date, creator=creator, left=left, broadcast=broadcast, verified=verified, megagroup=megagroup, restricted=restricted, signatures=signatures, min=min, scam=scam, has_link=has_link, has_geo=has_geo, slowmode_enabled=slowmode_enabled, call_active=call_active, call_not_empty=call_not_empty, fake=fake, gigagroup=gigagroup, noforwards=noforwards, access_hash=access_hash, username=username, restriction_reason=restriction_reason, admin_rights=admin_rights, banned_rights=banned_rights, default_banned_rights=default_banned_rights, participants_count=participants_count, live_msg_id=live_msg_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.creator else 0
        flags |= (1 << 2) if self.left else 0
        flags |= (1 << 5) if self.broadcast else 0
        flags |= (1 << 7) if self.verified else 0
        flags |= (1 << 8) if self.megagroup else 0
        flags |= (1 << 9) if self.restricted else 0
        flags |= (1 << 11) if self.signatures else 0
        flags |= (1 << 12) if self.min else 0
        flags |= (1 << 19) if self.scam else 0
        flags |= (1 << 20) if self.has_link else 0
        flags |= (1 << 21) if self.has_geo else 0
        flags |= (1 << 22) if self.slowmode_enabled else 0
        flags |= (1 << 23) if self.call_active else 0
        flags |= (1 << 24) if self.call_not_empty else 0
        flags |= (1 << 25) if self.fake else 0
        flags |= (1 << 26) if self.gigagroup else 0
        flags |= (1 << 27) if self.noforwards else 0
        flags |= (1 << 13) if self.access_hash is not None else 0
        flags |= (1 << 6) if self.username is not None else 0
        flags |= (1 << 9) if self.restriction_reason is not None else 0
        flags |= (1 << 14) if self.admin_rights is not None else 0
        flags |= (1 << 15) if self.banned_rights is not None else 0
        flags |= (1 << 18) if self.default_banned_rights is not None else 0
        flags |= (1 << 17) if self.participants_count is not None else 0
        flags |= (1 << 29) if self.live_msg_id is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        if self.access_hash is not None:
            data.write(Long(self.access_hash))
        
        data.write(String(self.title))
        
        if self.username is not None:
            data.write(String(self.username))
        
        data.write(self.photo.write())
        
        data.write(Int(self.date))
        
        if self.restriction_reason is not None:
            data.write(Vector(self.restriction_reason))
        
        if self.admin_rights is not None:
            data.write(self.admin_rights.write())
        
        if self.banned_rights is not None:
            data.write(self.banned_rights.write())
        
        if self.default_banned_rights is not None:
            data.write(self.default_banned_rights.write())
        
        if self.participants_count is not None:
            data.write(Int(self.participants_count))
        
        if self.live_msg_id is not None:
            data.write(Int(self.live_msg_id))
        
        return data.getvalue()
