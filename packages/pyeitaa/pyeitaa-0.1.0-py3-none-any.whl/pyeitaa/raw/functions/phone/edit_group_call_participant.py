from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class EditGroupCallParticipant(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5ad8c541``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        participant: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        muted (optional): ``bool``
        volume (optional): ``int`` ``32-bit``
        raise_hand (optional): ``bool``
        video_stopped (optional): ``bool``
        video_paused (optional): ``bool``
        presentation_paused (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["call", "participant", "muted", "volume", "raise_hand", "video_stopped", "video_paused", "presentation_paused"]

    ID = -0x5ad8c541
    QUALNAME = "functions.phone.EditGroupCallParticipant"

    def __init__(self, *, call: "raw.base.InputGroupCall", participant: "raw.base.InputPeer", muted: Optional[bool] = None, volume: Optional[int] = None, raise_hand: Optional[bool] = None, video_stopped: Optional[bool] = None, video_paused: Optional[bool] = None, presentation_paused: Optional[bool] = None) -> None:
        self.call = call  # InputGroupCall
        self.participant = participant  # InputPeer
        self.muted = muted  # flags.0?Bool
        self.volume = volume  # flags.1?int
        self.raise_hand = raise_hand  # flags.2?Bool
        self.video_stopped = video_stopped  # flags.3?Bool
        self.video_paused = video_paused  # flags.4?Bool
        self.presentation_paused = presentation_paused  # flags.5?Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        call = TLObject.read(data)
        
        participant = TLObject.read(data)
        
        muted = Bool.read(data) if flags & (1 << 0) else None
        volume = Int.read(data) if flags & (1 << 1) else None
        raise_hand = Bool.read(data) if flags & (1 << 2) else None
        video_stopped = Bool.read(data) if flags & (1 << 3) else None
        video_paused = Bool.read(data) if flags & (1 << 4) else None
        presentation_paused = Bool.read(data) if flags & (1 << 5) else None
        return EditGroupCallParticipant(call=call, participant=participant, muted=muted, volume=volume, raise_hand=raise_hand, video_stopped=video_stopped, video_paused=video_paused, presentation_paused=presentation_paused)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.muted is not None else 0
        flags |= (1 << 1) if self.volume is not None else 0
        flags |= (1 << 2) if self.raise_hand is not None else 0
        flags |= (1 << 3) if self.video_stopped is not None else 0
        flags |= (1 << 4) if self.video_paused is not None else 0
        flags |= (1 << 5) if self.presentation_paused is not None else 0
        data.write(Int(flags))
        
        data.write(self.call.write())
        
        data.write(self.participant.write())
        
        if self.muted is not None:
            data.write(Bool(self.muted))
        
        if self.volume is not None:
            data.write(Int(self.volume))
        
        if self.raise_hand is not None:
            data.write(Bool(self.raise_hand))
        
        if self.video_stopped is not None:
            data.write(Bool(self.video_stopped))
        
        if self.video_paused is not None:
            data.write(Bool(self.video_paused))
        
        if self.presentation_paused is not None:
            data.write(Bool(self.presentation_paused))
        
        return data.getvalue()
