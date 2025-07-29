from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PrivacyRules(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.PrivacyRules`.

    Details:
        - Layer: ``135``
        - ID: ``0x50a04e45``

    Parameters:
        rules: List of :obj:`PrivacyRule <pyeitaa.raw.base.PrivacyRule>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetPrivacy <pyeitaa.raw.functions.account.GetPrivacy>`
            - :obj:`account.SetPrivacy <pyeitaa.raw.functions.account.SetPrivacy>`
    """

    __slots__: List[str] = ["rules", "chats", "users"]

    ID = 0x50a04e45
    QUALNAME = "types.account.PrivacyRules"

    def __init__(self, *, rules: List["raw.base.PrivacyRule"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.rules = rules  # Vector<PrivacyRule>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        rules = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return PrivacyRules(rules=rules, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.rules))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
