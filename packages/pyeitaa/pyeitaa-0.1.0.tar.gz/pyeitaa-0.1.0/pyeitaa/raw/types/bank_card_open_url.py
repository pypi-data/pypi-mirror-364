from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class BankCardOpenUrl(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.BankCardOpenUrl`.

    Details:
        - Layer: ``135``
        - ID: ``-0xa97fd76``

    Parameters:
        url: ``str``
        name: ``str``
    """

    __slots__: List[str] = ["url", "name"]

    ID = -0xa97fd76
    QUALNAME = "types.BankCardOpenUrl"

    def __init__(self, *, url: str, name: str) -> None:
        self.url = url  # string
        self.name = name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        name = String.read(data)
        
        return BankCardOpenUrl(url=url, name=name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        data.write(String(self.name))
        
        return data.getvalue()
