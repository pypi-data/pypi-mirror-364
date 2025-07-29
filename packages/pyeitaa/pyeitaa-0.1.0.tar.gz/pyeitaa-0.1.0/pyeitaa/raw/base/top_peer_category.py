from typing import Union
from pyeitaa import raw

TopPeerCategory = Union[raw.types.TopPeerCategoryBotsInline, raw.types.TopPeerCategoryBotsPM, raw.types.TopPeerCategoryChannels, raw.types.TopPeerCategoryCorrespondents, raw.types.TopPeerCategoryForwardChats, raw.types.TopPeerCategoryForwardUsers, raw.types.TopPeerCategoryGroups, raw.types.TopPeerCategoryPhoneCalls]


# noinspection PyRedeclaration
class TopPeerCategory:
    """This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`TopPeerCategoryBotsInline <pyeitaa.raw.types.TopPeerCategoryBotsInline>`
            - :obj:`TopPeerCategoryBotsPM <pyeitaa.raw.types.TopPeerCategoryBotsPM>`
            - :obj:`TopPeerCategoryChannels <pyeitaa.raw.types.TopPeerCategoryChannels>`
            - :obj:`TopPeerCategoryCorrespondents <pyeitaa.raw.types.TopPeerCategoryCorrespondents>`
            - :obj:`TopPeerCategoryForwardChats <pyeitaa.raw.types.TopPeerCategoryForwardChats>`
            - :obj:`TopPeerCategoryForwardUsers <pyeitaa.raw.types.TopPeerCategoryForwardUsers>`
            - :obj:`TopPeerCategoryGroups <pyeitaa.raw.types.TopPeerCategoryGroups>`
            - :obj:`TopPeerCategoryPhoneCalls <pyeitaa.raw.types.TopPeerCategoryPhoneCalls>`
    """

    QUALNAME = "pyeitaa.raw.base.TopPeerCategory"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
