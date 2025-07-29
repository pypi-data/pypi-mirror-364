from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ChatBannedRights(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatBannedRights`.

    Details:
        - Layer: ``135``
        - ID: ``-0x60edfbe8``

    Parameters:
        until_date: ``int`` ``32-bit``
        view_messages (optional): ``bool``
        send_messages (optional): ``bool``
        send_media (optional): ``bool``
        send_stickers (optional): ``bool``
        send_gifs (optional): ``bool``
        send_games (optional): ``bool``
        send_inline (optional): ``bool``
        send_polls (optional): ``bool``
        change_info (optional): ``bool``
        embed_links (optional): ``bool``
        view_participants (optional): ``bool``
        invite_users (optional): ``bool``
        pin_messages (optional): ``bool``
        send_forwarded_messages (optional): ``bool``
    """

    __slots__: List[str] = ["until_date", "view_messages", "send_messages", "send_media", "send_stickers", "send_gifs", "send_games", "send_inline", "send_polls", "change_info", "embed_links", "view_participants", "invite_users", "pin_messages", "send_forwarded_messages"]

    ID = -0x60edfbe8
    QUALNAME = "types.ChatBannedRights"

    def __init__(self, *, until_date: int, view_messages: Optional[bool] = None, send_messages: Optional[bool] = None, send_media: Optional[bool] = None, send_stickers: Optional[bool] = None, send_gifs: Optional[bool] = None, send_games: Optional[bool] = None, send_inline: Optional[bool] = None, send_polls: Optional[bool] = None, change_info: Optional[bool] = None, embed_links: Optional[bool] = None, view_participants: Optional[bool] = None, invite_users: Optional[bool] = None, pin_messages: Optional[bool] = None, send_forwarded_messages: Optional[bool] = None) -> None:
        self.until_date = until_date  # int
        self.view_messages = view_messages  # flags.0?true
        self.send_messages = send_messages  # flags.1?true
        self.send_media = send_media  # flags.2?true
        self.send_stickers = send_stickers  # flags.3?true
        self.send_gifs = send_gifs  # flags.4?true
        self.send_games = send_games  # flags.5?true
        self.send_inline = send_inline  # flags.6?true
        self.send_polls = send_polls  # flags.8?true
        self.change_info = change_info  # flags.10?true
        self.embed_links = embed_links  # flags.12?true
        self.view_participants = view_participants  # flags.13?true
        self.invite_users = invite_users  # flags.15?true
        self.pin_messages = pin_messages  # flags.17?true
        self.send_forwarded_messages = send_forwarded_messages  # flags.11?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        view_messages = True if flags & (1 << 0) else False
        send_messages = True if flags & (1 << 1) else False
        send_media = True if flags & (1 << 2) else False
        send_stickers = True if flags & (1 << 3) else False
        send_gifs = True if flags & (1 << 4) else False
        send_games = True if flags & (1 << 5) else False
        send_inline = True if flags & (1 << 6) else False
        send_polls = True if flags & (1 << 8) else False
        change_info = True if flags & (1 << 10) else False
        embed_links = True if flags & (1 << 12) else False
        view_participants = True if flags & (1 << 13) else False
        invite_users = True if flags & (1 << 15) else False
        pin_messages = True if flags & (1 << 17) else False
        send_forwarded_messages = True if flags & (1 << 11) else False
        until_date = Int.read(data)
        
        return ChatBannedRights(until_date=until_date, view_messages=view_messages, send_messages=send_messages, send_media=send_media, send_stickers=send_stickers, send_gifs=send_gifs, send_games=send_games, send_inline=send_inline, send_polls=send_polls, change_info=change_info, embed_links=embed_links, view_participants=view_participants, invite_users=invite_users, pin_messages=pin_messages, send_forwarded_messages=send_forwarded_messages)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.view_messages else 0
        flags |= (1 << 1) if self.send_messages else 0
        flags |= (1 << 2) if self.send_media else 0
        flags |= (1 << 3) if self.send_stickers else 0
        flags |= (1 << 4) if self.send_gifs else 0
        flags |= (1 << 5) if self.send_games else 0
        flags |= (1 << 6) if self.send_inline else 0
        flags |= (1 << 8) if self.send_polls else 0
        flags |= (1 << 10) if self.change_info else 0
        flags |= (1 << 12) if self.embed_links else 0
        flags |= (1 << 13) if self.view_participants else 0
        flags |= (1 << 15) if self.invite_users else 0
        flags |= (1 << 17) if self.pin_messages else 0
        flags |= (1 << 11) if self.send_forwarded_messages else 0
        data.write(Int(flags))
        
        data.write(Int(self.until_date))
        
        return data.getvalue()
