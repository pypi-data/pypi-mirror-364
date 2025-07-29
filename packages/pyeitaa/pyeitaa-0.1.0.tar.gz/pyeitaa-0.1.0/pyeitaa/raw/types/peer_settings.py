from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class PeerSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PeerSettings`.

    Details:
        - Layer: ``135``
        - ID: ``0x733f2961``

    Parameters:
        report_spam (optional): ``bool``
        add_contact (optional): ``bool``
        block_contact (optional): ``bool``
        share_contact (optional): ``bool``
        need_contacts_exception (optional): ``bool``
        report_geo (optional): ``bool``
        autoarchived (optional): ``bool``
        invite_members (optional): ``bool``
        geo_distance (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetPeerSettings <pyeitaa.raw.functions.messages.GetPeerSettings>`
    """

    __slots__: List[str] = ["report_spam", "add_contact", "block_contact", "share_contact", "need_contacts_exception", "report_geo", "autoarchived", "invite_members", "geo_distance"]

    ID = 0x733f2961
    QUALNAME = "types.PeerSettings"

    def __init__(self, *, report_spam: Optional[bool] = None, add_contact: Optional[bool] = None, block_contact: Optional[bool] = None, share_contact: Optional[bool] = None, need_contacts_exception: Optional[bool] = None, report_geo: Optional[bool] = None, autoarchived: Optional[bool] = None, invite_members: Optional[bool] = None, geo_distance: Optional[int] = None) -> None:
        self.report_spam = report_spam  # flags.0?true
        self.add_contact = add_contact  # flags.1?true
        self.block_contact = block_contact  # flags.2?true
        self.share_contact = share_contact  # flags.3?true
        self.need_contacts_exception = need_contacts_exception  # flags.4?true
        self.report_geo = report_geo  # flags.5?true
        self.autoarchived = autoarchived  # flags.7?true
        self.invite_members = invite_members  # flags.8?true
        self.geo_distance = geo_distance  # flags.6?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        report_spam = True if flags & (1 << 0) else False
        add_contact = True if flags & (1 << 1) else False
        block_contact = True if flags & (1 << 2) else False
        share_contact = True if flags & (1 << 3) else False
        need_contacts_exception = True if flags & (1 << 4) else False
        report_geo = True if flags & (1 << 5) else False
        autoarchived = True if flags & (1 << 7) else False
        invite_members = True if flags & (1 << 8) else False
        geo_distance = Int.read(data) if flags & (1 << 6) else None
        return PeerSettings(report_spam=report_spam, add_contact=add_contact, block_contact=block_contact, share_contact=share_contact, need_contacts_exception=need_contacts_exception, report_geo=report_geo, autoarchived=autoarchived, invite_members=invite_members, geo_distance=geo_distance)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.report_spam else 0
        flags |= (1 << 1) if self.add_contact else 0
        flags |= (1 << 2) if self.block_contact else 0
        flags |= (1 << 3) if self.share_contact else 0
        flags |= (1 << 4) if self.need_contacts_exception else 0
        flags |= (1 << 5) if self.report_geo else 0
        flags |= (1 << 7) if self.autoarchived else 0
        flags |= (1 << 8) if self.invite_members else 0
        flags |= (1 << 6) if self.geo_distance is not None else 0
        data.write(Int(flags))
        
        if self.geo_distance is not None:
            data.write(Int(self.geo_distance))
        
        return data.getvalue()
