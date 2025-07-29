from typing import Union
from pyeitaa import raw

ChannelParticipantsFilter = Union[raw.types.ChannelParticipantsAdmins, raw.types.ChannelParticipantsBanned, raw.types.ChannelParticipantsBots, raw.types.ChannelParticipantsContacts, raw.types.ChannelParticipantsKicked, raw.types.ChannelParticipantsMentions, raw.types.ChannelParticipantsRecent, raw.types.ChannelParticipantsSearch]


# noinspection PyRedeclaration
class ChannelParticipantsFilter:
    """This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChannelParticipantsAdmins <pyeitaa.raw.types.ChannelParticipantsAdmins>`
            - :obj:`ChannelParticipantsBanned <pyeitaa.raw.types.ChannelParticipantsBanned>`
            - :obj:`ChannelParticipantsBots <pyeitaa.raw.types.ChannelParticipantsBots>`
            - :obj:`ChannelParticipantsContacts <pyeitaa.raw.types.ChannelParticipantsContacts>`
            - :obj:`ChannelParticipantsKicked <pyeitaa.raw.types.ChannelParticipantsKicked>`
            - :obj:`ChannelParticipantsMentions <pyeitaa.raw.types.ChannelParticipantsMentions>`
            - :obj:`ChannelParticipantsRecent <pyeitaa.raw.types.ChannelParticipantsRecent>`
            - :obj:`ChannelParticipantsSearch <pyeitaa.raw.types.ChannelParticipantsSearch>`
    """

    QUALNAME = "pyeitaa.raw.base.ChannelParticipantsFilter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
