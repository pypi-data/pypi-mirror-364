from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class GlobalPrivacySettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.GlobalPrivacySettings`.

    Details:
        - Layer: ``135``
        - ID: ``-0x415d0bdc``

    Parameters:
        archive_and_mute_new_noncontact_peers (optional): ``bool``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetGlobalPrivacySettings <pyeitaa.raw.functions.account.GetGlobalPrivacySettings>`
            - :obj:`account.SetGlobalPrivacySettings <pyeitaa.raw.functions.account.SetGlobalPrivacySettings>`
    """

    __slots__: List[str] = ["archive_and_mute_new_noncontact_peers"]

    ID = -0x415d0bdc
    QUALNAME = "types.GlobalPrivacySettings"

    def __init__(self, *, archive_and_mute_new_noncontact_peers: Optional[bool] = None) -> None:
        self.archive_and_mute_new_noncontact_peers = archive_and_mute_new_noncontact_peers  # flags.0?Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        archive_and_mute_new_noncontact_peers = Bool.read(data) if flags & (1 << 0) else None
        return GlobalPrivacySettings(archive_and_mute_new_noncontact_peers=archive_and_mute_new_noncontact_peers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.archive_and_mute_new_noncontact_peers is not None else 0
        data.write(Int(flags))
        
        if self.archive_and_mute_new_noncontact_peers is not None:
            data.write(Bool(self.archive_and_mute_new_noncontact_peers))
        
        return data.getvalue()
