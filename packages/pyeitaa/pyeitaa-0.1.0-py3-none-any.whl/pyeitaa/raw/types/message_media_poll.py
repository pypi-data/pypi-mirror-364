from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageMediaPoll(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x4bd6e798``

    Parameters:
        poll: :obj:`Poll <pyeitaa.raw.base.Poll>`
        results: :obj:`PollResults <pyeitaa.raw.base.PollResults>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["poll", "results"]

    ID = 0x4bd6e798
    QUALNAME = "types.MessageMediaPoll"

    def __init__(self, *, poll: "raw.base.Poll", results: "raw.base.PollResults") -> None:
        self.poll = poll  # Poll
        self.results = results  # PollResults

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        poll = TLObject.read(data)
        
        results = TLObject.read(data)
        
        return MessageMediaPoll(poll=poll, results=results)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.poll.write())
        
        data.write(self.results.write())
        
        return data.getvalue()
