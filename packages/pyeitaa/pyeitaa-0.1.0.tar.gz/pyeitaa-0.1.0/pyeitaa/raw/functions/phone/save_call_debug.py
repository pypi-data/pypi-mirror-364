from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SaveCallDebug(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x277add7e``

    Parameters:
        peer: :obj:`InputPhoneCall <pyeitaa.raw.base.InputPhoneCall>`
        debug: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "debug"]

    ID = 0x277add7e
    QUALNAME = "functions.phone.SaveCallDebug"

    def __init__(self, *, peer: "raw.base.InputPhoneCall", debug: "raw.base.DataJSON") -> None:
        self.peer = peer  # InputPhoneCall
        self.debug = debug  # DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        debug = TLObject.read(data)
        
        return SaveCallDebug(peer=peer, debug=debug)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(self.debug.write())
        
        return data.getvalue()
