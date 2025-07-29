from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MegagroupStats(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.stats.MegagroupStats`.

    Details:
        - Layer: ``135``
        - ID: ``-0x108006ea``

    Parameters:
        period: :obj:`StatsDateRangeDays <pyeitaa.raw.base.StatsDateRangeDays>`
        members: :obj:`StatsAbsValueAndPrev <pyeitaa.raw.base.StatsAbsValueAndPrev>`
        messages: :obj:`StatsAbsValueAndPrev <pyeitaa.raw.base.StatsAbsValueAndPrev>`
        viewers: :obj:`StatsAbsValueAndPrev <pyeitaa.raw.base.StatsAbsValueAndPrev>`
        posters: :obj:`StatsAbsValueAndPrev <pyeitaa.raw.base.StatsAbsValueAndPrev>`
        growth_graph: :obj:`StatsGraph <pyeitaa.raw.base.StatsGraph>`
        members_graph: :obj:`StatsGraph <pyeitaa.raw.base.StatsGraph>`
        new_members_by_source_graph: :obj:`StatsGraph <pyeitaa.raw.base.StatsGraph>`
        languages_graph: :obj:`StatsGraph <pyeitaa.raw.base.StatsGraph>`
        messages_graph: :obj:`StatsGraph <pyeitaa.raw.base.StatsGraph>`
        actions_graph: :obj:`StatsGraph <pyeitaa.raw.base.StatsGraph>`
        top_hours_graph: :obj:`StatsGraph <pyeitaa.raw.base.StatsGraph>`
        weekdays_graph: :obj:`StatsGraph <pyeitaa.raw.base.StatsGraph>`
        top_posters: List of :obj:`StatsGroupTopPoster <pyeitaa.raw.base.StatsGroupTopPoster>`
        top_admins: List of :obj:`StatsGroupTopAdmin <pyeitaa.raw.base.StatsGroupTopAdmin>`
        top_inviters: List of :obj:`StatsGroupTopInviter <pyeitaa.raw.base.StatsGroupTopInviter>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.GetMegagroupStats <pyeitaa.raw.functions.stats.GetMegagroupStats>`
    """

    __slots__: List[str] = ["period", "members", "messages", "viewers", "posters", "growth_graph", "members_graph", "new_members_by_source_graph", "languages_graph", "messages_graph", "actions_graph", "top_hours_graph", "weekdays_graph", "top_posters", "top_admins", "top_inviters", "users"]

    ID = -0x108006ea
    QUALNAME = "types.stats.MegagroupStats"

    def __init__(self, *, period: "raw.base.StatsDateRangeDays", members: "raw.base.StatsAbsValueAndPrev", messages: "raw.base.StatsAbsValueAndPrev", viewers: "raw.base.StatsAbsValueAndPrev", posters: "raw.base.StatsAbsValueAndPrev", growth_graph: "raw.base.StatsGraph", members_graph: "raw.base.StatsGraph", new_members_by_source_graph: "raw.base.StatsGraph", languages_graph: "raw.base.StatsGraph", messages_graph: "raw.base.StatsGraph", actions_graph: "raw.base.StatsGraph", top_hours_graph: "raw.base.StatsGraph", weekdays_graph: "raw.base.StatsGraph", top_posters: List["raw.base.StatsGroupTopPoster"], top_admins: List["raw.base.StatsGroupTopAdmin"], top_inviters: List["raw.base.StatsGroupTopInviter"], users: List["raw.base.User"]) -> None:
        self.period = period  # StatsDateRangeDays
        self.members = members  # StatsAbsValueAndPrev
        self.messages = messages  # StatsAbsValueAndPrev
        self.viewers = viewers  # StatsAbsValueAndPrev
        self.posters = posters  # StatsAbsValueAndPrev
        self.growth_graph = growth_graph  # StatsGraph
        self.members_graph = members_graph  # StatsGraph
        self.new_members_by_source_graph = new_members_by_source_graph  # StatsGraph
        self.languages_graph = languages_graph  # StatsGraph
        self.messages_graph = messages_graph  # StatsGraph
        self.actions_graph = actions_graph  # StatsGraph
        self.top_hours_graph = top_hours_graph  # StatsGraph
        self.weekdays_graph = weekdays_graph  # StatsGraph
        self.top_posters = top_posters  # Vector<StatsGroupTopPoster>
        self.top_admins = top_admins  # Vector<StatsGroupTopAdmin>
        self.top_inviters = top_inviters  # Vector<StatsGroupTopInviter>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        period = TLObject.read(data)
        
        members = TLObject.read(data)
        
        messages = TLObject.read(data)
        
        viewers = TLObject.read(data)
        
        posters = TLObject.read(data)
        
        growth_graph = TLObject.read(data)
        
        members_graph = TLObject.read(data)
        
        new_members_by_source_graph = TLObject.read(data)
        
        languages_graph = TLObject.read(data)
        
        messages_graph = TLObject.read(data)
        
        actions_graph = TLObject.read(data)
        
        top_hours_graph = TLObject.read(data)
        
        weekdays_graph = TLObject.read(data)
        
        top_posters = TLObject.read(data)
        
        top_admins = TLObject.read(data)
        
        top_inviters = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return MegagroupStats(period=period, members=members, messages=messages, viewers=viewers, posters=posters, growth_graph=growth_graph, members_graph=members_graph, new_members_by_source_graph=new_members_by_source_graph, languages_graph=languages_graph, messages_graph=messages_graph, actions_graph=actions_graph, top_hours_graph=top_hours_graph, weekdays_graph=weekdays_graph, top_posters=top_posters, top_admins=top_admins, top_inviters=top_inviters, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.period.write())
        
        data.write(self.members.write())
        
        data.write(self.messages.write())
        
        data.write(self.viewers.write())
        
        data.write(self.posters.write())
        
        data.write(self.growth_graph.write())
        
        data.write(self.members_graph.write())
        
        data.write(self.new_members_by_source_graph.write())
        
        data.write(self.languages_graph.write())
        
        data.write(self.messages_graph.write())
        
        data.write(self.actions_graph.write())
        
        data.write(self.top_hours_graph.write())
        
        data.write(self.weekdays_graph.write())
        
        data.write(Vector(self.top_posters))
        
        data.write(Vector(self.top_admins))
        
        data.write(Vector(self.top_inviters))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
