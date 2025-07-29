from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PromoData(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.help.PromoData`.

    Details:
        - Layer: ``135``
        - ID: ``-0x73c686c1``

    Parameters:
        expires: ``int`` ``32-bit``
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        proxy (optional): ``bool``
        psa_type (optional): ``str``
        psa_message (optional): ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetPromoData <pyeitaa.raw.functions.help.GetPromoData>`
    """

    __slots__: List[str] = ["expires", "peer", "chats", "users", "proxy", "psa_type", "psa_message"]

    ID = -0x73c686c1
    QUALNAME = "types.help.PromoData"

    def __init__(self, *, expires: int, peer: "raw.base.Peer", chats: List["raw.base.Chat"], users: List["raw.base.User"], proxy: Optional[bool] = None, psa_type: Optional[str] = None, psa_message: Optional[str] = None) -> None:
        self.expires = expires  # int
        self.peer = peer  # Peer
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.proxy = proxy  # flags.0?true
        self.psa_type = psa_type  # flags.1?string
        self.psa_message = psa_message  # flags.2?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        proxy = True if flags & (1 << 0) else False
        expires = Int.read(data)
        
        peer = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        psa_type = String.read(data) if flags & (1 << 1) else None
        psa_message = String.read(data) if flags & (1 << 2) else None
        return PromoData(expires=expires, peer=peer, chats=chats, users=users, proxy=proxy, psa_type=psa_type, psa_message=psa_message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.proxy else 0
        flags |= (1 << 1) if self.psa_type is not None else 0
        flags |= (1 << 2) if self.psa_message is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.expires))
        
        data.write(self.peer.write())
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        if self.psa_type is not None:
            data.write(String(self.psa_type))
        
        if self.psa_message is not None:
            data.write(String(self.psa_message))
        
        return data.getvalue()
