from typing import Union
from pyeitaa import raw

AdsLocation = Union[raw.types.AdsInputAdsLocationChatMembers, raw.types.AdsInputAdsLocationContacts, raw.types.AdsInputAdsLocationDialog, raw.types.AdsInputAdsLocationRecommend, raw.types.AdsInputAdsLocationTrends]


# noinspection PyRedeclaration
class AdsLocation:
    """This base type has 5 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`AdsInputAdsLocationChatMembers <pyeitaa.raw.types.AdsInputAdsLocationChatMembers>`
            - :obj:`AdsInputAdsLocationContacts <pyeitaa.raw.types.AdsInputAdsLocationContacts>`
            - :obj:`AdsInputAdsLocationDialog <pyeitaa.raw.types.AdsInputAdsLocationDialog>`
            - :obj:`AdsInputAdsLocationRecommend <pyeitaa.raw.types.AdsInputAdsLocationRecommend>`
            - :obj:`AdsInputAdsLocationTrends <pyeitaa.raw.types.AdsInputAdsLocationTrends>`
    """

    QUALNAME = "pyeitaa.raw.base.AdsLocation"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
