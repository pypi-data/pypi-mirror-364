from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UrlAuthResultRequest(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.UrlAuthResult`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6d2cc5f2``

    Parameters:
        bot: :obj:`User <pyeitaa.raw.base.User>`
        domain: ``str``
        request_write_access (optional): ``bool``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.RequestUrlAuth <pyeitaa.raw.functions.messages.RequestUrlAuth>`
            - :obj:`messages.AcceptUrlAuth <pyeitaa.raw.functions.messages.AcceptUrlAuth>`
    """

    __slots__: List[str] = ["bot", "domain", "request_write_access"]

    ID = -0x6d2cc5f2
    QUALNAME = "types.UrlAuthResultRequest"

    def __init__(self, *, bot: "raw.base.User", domain: str, request_write_access: Optional[bool] = None) -> None:
        self.bot = bot  # User
        self.domain = domain  # string
        self.request_write_access = request_write_access  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        request_write_access = True if flags & (1 << 0) else False
        bot = TLObject.read(data)
        
        domain = String.read(data)
        
        return UrlAuthResultRequest(bot=bot, domain=domain, request_write_access=request_write_access)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.request_write_access else 0
        data.write(Int(flags))
        
        data.write(self.bot.write())
        
        data.write(String(self.domain))
        
        return data.getvalue()
