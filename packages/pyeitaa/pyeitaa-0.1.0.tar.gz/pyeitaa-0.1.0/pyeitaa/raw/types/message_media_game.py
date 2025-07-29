from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageMediaGame(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x24e6ff8``

    Parameters:
        game: :obj:`Game <pyeitaa.raw.base.Game>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["game"]

    ID = -0x24e6ff8
    QUALNAME = "types.MessageMediaGame"

    def __init__(self, *, game: "raw.base.Game") -> None:
        self.game = game  # Game

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        game = TLObject.read(data)
        
        return MessageMediaGame(game=game)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.game.write())
        
        return data.getvalue()
