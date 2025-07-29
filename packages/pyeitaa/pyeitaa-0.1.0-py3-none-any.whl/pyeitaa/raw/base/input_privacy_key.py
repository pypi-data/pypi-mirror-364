from typing import Union
from pyeitaa import raw

InputPrivacyKey = Union[raw.types.InputPrivacyKeyAddedByPhone, raw.types.InputPrivacyKeyChatInvite, raw.types.InputPrivacyKeyForwards, raw.types.InputPrivacyKeyPhoneCall, raw.types.InputPrivacyKeyPhoneNumber, raw.types.InputPrivacyKeyPhoneP2P, raw.types.InputPrivacyKeyProfilePhoto, raw.types.InputPrivacyKeyStatusTimestamp]


# noinspection PyRedeclaration
class InputPrivacyKey:
    """This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputPrivacyKeyAddedByPhone <pyeitaa.raw.types.InputPrivacyKeyAddedByPhone>`
            - :obj:`InputPrivacyKeyChatInvite <pyeitaa.raw.types.InputPrivacyKeyChatInvite>`
            - :obj:`InputPrivacyKeyForwards <pyeitaa.raw.types.InputPrivacyKeyForwards>`
            - :obj:`InputPrivacyKeyPhoneCall <pyeitaa.raw.types.InputPrivacyKeyPhoneCall>`
            - :obj:`InputPrivacyKeyPhoneNumber <pyeitaa.raw.types.InputPrivacyKeyPhoneNumber>`
            - :obj:`InputPrivacyKeyPhoneP2P <pyeitaa.raw.types.InputPrivacyKeyPhoneP2P>`
            - :obj:`InputPrivacyKeyProfilePhoto <pyeitaa.raw.types.InputPrivacyKeyProfilePhoto>`
            - :obj:`InputPrivacyKeyStatusTimestamp <pyeitaa.raw.types.InputPrivacyKeyStatusTimestamp>`
    """

    QUALNAME = "pyeitaa.raw.base.InputPrivacyKey"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
