from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SetCallRating(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x59ead627``

    Parameters:
        peer: :obj:`InputPhoneCall <pyeitaa.raw.base.InputPhoneCall>`
        rating: ``int`` ``32-bit``
        comment: ``str``
        user_initiative (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "rating", "comment", "user_initiative"]

    ID = 0x59ead627
    QUALNAME = "functions.phone.SetCallRating"

    def __init__(self, *, peer: "raw.base.InputPhoneCall", rating: int, comment: str, user_initiative: Optional[bool] = None) -> None:
        self.peer = peer  # InputPhoneCall
        self.rating = rating  # int
        self.comment = comment  # string
        self.user_initiative = user_initiative  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        user_initiative = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        rating = Int.read(data)
        
        comment = String.read(data)
        
        return SetCallRating(peer=peer, rating=rating, comment=comment, user_initiative=user_initiative)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.user_initiative else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Int(self.rating))
        
        data.write(String(self.comment))
        
        return data.getvalue()
