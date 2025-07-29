from typing import Union
from pyeitaa import raw

PrivacyKey = Union[raw.types.PrivacyKeyAddedByPhone, raw.types.PrivacyKeyChatInvite, raw.types.PrivacyKeyForwards, raw.types.PrivacyKeyPhoneCall, raw.types.PrivacyKeyPhoneNumber, raw.types.PrivacyKeyPhoneP2P, raw.types.PrivacyKeyProfilePhoto, raw.types.PrivacyKeyStatusTimestamp]


# noinspection PyRedeclaration
class PrivacyKey:
    """This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PrivacyKeyAddedByPhone <pyeitaa.raw.types.PrivacyKeyAddedByPhone>`
            - :obj:`PrivacyKeyChatInvite <pyeitaa.raw.types.PrivacyKeyChatInvite>`
            - :obj:`PrivacyKeyForwards <pyeitaa.raw.types.PrivacyKeyForwards>`
            - :obj:`PrivacyKeyPhoneCall <pyeitaa.raw.types.PrivacyKeyPhoneCall>`
            - :obj:`PrivacyKeyPhoneNumber <pyeitaa.raw.types.PrivacyKeyPhoneNumber>`
            - :obj:`PrivacyKeyPhoneP2P <pyeitaa.raw.types.PrivacyKeyPhoneP2P>`
            - :obj:`PrivacyKeyProfilePhoto <pyeitaa.raw.types.PrivacyKeyProfilePhoto>`
            - :obj:`PrivacyKeyStatusTimestamp <pyeitaa.raw.types.PrivacyKeyStatusTimestamp>`
    """

    QUALNAME = "pyeitaa.raw.base.PrivacyKey"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
