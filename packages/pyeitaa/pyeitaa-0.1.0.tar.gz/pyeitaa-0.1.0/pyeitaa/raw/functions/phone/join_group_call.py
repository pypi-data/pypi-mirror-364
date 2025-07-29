from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class JoinGroupCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4ecd0085``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        join_as: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        params: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
        muted (optional): ``bool``
        video_stopped (optional): ``bool``
        invite_hash (optional): ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "join_as", "params", "muted", "video_stopped", "invite_hash"]

    ID = -0x4ecd0085
    QUALNAME = "functions.phone.JoinGroupCall"

    def __init__(self, *, call: "raw.base.InputGroupCall", join_as: "raw.base.InputPeer", params: "raw.base.DataJSON", muted: Optional[bool] = None, video_stopped: Optional[bool] = None, invite_hash: Optional[str] = None) -> None:
        self.call = call  # InputGroupCall
        self.join_as = join_as  # InputPeer
        self.params = params  # DataJSON
        self.muted = muted  # flags.0?true
        self.video_stopped = video_stopped  # flags.2?true
        self.invite_hash = invite_hash  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        muted = True if flags & (1 << 0) else False
        video_stopped = True if flags & (1 << 2) else False
        call = TLObject.read(data)
        
        join_as = TLObject.read(data)
        
        invite_hash = String.read(data) if flags & (1 << 1) else None
        params = TLObject.read(data)
        
        return JoinGroupCall(call=call, join_as=join_as, params=params, muted=muted, video_stopped=video_stopped, invite_hash=invite_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.muted else 0
        flags |= (1 << 2) if self.video_stopped else 0
        flags |= (1 << 1) if self.invite_hash is not None else 0
        data.write(Int(flags))
        
        data.write(self.call.write())
        
        data.write(self.join_as.write())
        
        if self.invite_hash is not None:
            data.write(String(self.invite_hash))
        
        data.write(self.params.write())
        
        return data.getvalue()
