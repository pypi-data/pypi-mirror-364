from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class BankCardData(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.payments.BankCardData`.

    Details:
        - Layer: ``135``
        - ID: ``0x3e24e573``

    Parameters:
        title: ``str``
        open_urls: List of :obj:`BankCardOpenUrl <pyeitaa.raw.base.BankCardOpenUrl>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.GetBankCardData <pyeitaa.raw.functions.payments.GetBankCardData>`
    """

    __slots__: List[str] = ["title", "open_urls"]

    ID = 0x3e24e573
    QUALNAME = "types.payments.BankCardData"

    def __init__(self, *, title: str, open_urls: List["raw.base.BankCardOpenUrl"]) -> None:
        self.title = title  # string
        self.open_urls = open_urls  # Vector<BankCardOpenUrl>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        title = String.read(data)
        
        open_urls = TLObject.read(data)
        
        return BankCardData(title=title, open_urls=open_urls)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.title))
        
        data.write(Vector(self.open_urls))
        
        return data.getvalue()
