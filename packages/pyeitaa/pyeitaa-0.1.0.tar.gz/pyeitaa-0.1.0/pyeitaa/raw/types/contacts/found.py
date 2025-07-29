from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Found(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.contacts.Found`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4cecb263``

    Parameters:
        my_results: List of :obj:`Peer <pyeitaa.raw.base.Peer>`
        results: List of :obj:`Peer <pyeitaa.raw.base.Peer>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`contacts.Search <pyeitaa.raw.functions.contacts.Search>`
    """

    __slots__: List[str] = ["my_results", "results", "chats", "users"]

    ID = -0x4cecb263
    QUALNAME = "types.contacts.Found"

    def __init__(self, *, my_results: List["raw.base.Peer"], results: List["raw.base.Peer"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.my_results = my_results  # Vector<Peer>
        self.results = results  # Vector<Peer>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        my_results = TLObject.read(data)
        
        results = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return Found(my_results=my_results, results=results, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.my_results))
        
        data.write(Vector(self.results))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
