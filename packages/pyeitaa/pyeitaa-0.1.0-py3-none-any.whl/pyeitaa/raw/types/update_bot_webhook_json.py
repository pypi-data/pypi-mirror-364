from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateBotWebhookJSON(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7ce83f3d``

    Parameters:
        data: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
    """

    __slots__: List[str] = ["data"]

    ID = -0x7ce83f3d
    QUALNAME = "types.UpdateBotWebhookJSON"

    def __init__(self, *, data: "raw.base.DataJSON") -> None:
        self.data = data  # DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        data = TLObject.read(data)
        
        return UpdateBotWebhookJSON(data=data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.data.write())
        
        return data.getvalue()
