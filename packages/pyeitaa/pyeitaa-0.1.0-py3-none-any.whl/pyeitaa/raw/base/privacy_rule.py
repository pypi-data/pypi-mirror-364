from typing import Union
from pyeitaa import raw

PrivacyRule = Union[raw.types.PrivacyValueAllowAll, raw.types.PrivacyValueAllowChatParticipants, raw.types.PrivacyValueAllowContacts, raw.types.PrivacyValueAllowUsers, raw.types.PrivacyValueDisallowAll, raw.types.PrivacyValueDisallowChatParticipants, raw.types.PrivacyValueDisallowContacts, raw.types.PrivacyValueDisallowUsers]


# noinspection PyRedeclaration
class PrivacyRule:
    """This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PrivacyValueAllowAll <pyeitaa.raw.types.PrivacyValueAllowAll>`
            - :obj:`PrivacyValueAllowChatParticipants <pyeitaa.raw.types.PrivacyValueAllowChatParticipants>`
            - :obj:`PrivacyValueAllowContacts <pyeitaa.raw.types.PrivacyValueAllowContacts>`
            - :obj:`PrivacyValueAllowUsers <pyeitaa.raw.types.PrivacyValueAllowUsers>`
            - :obj:`PrivacyValueDisallowAll <pyeitaa.raw.types.PrivacyValueDisallowAll>`
            - :obj:`PrivacyValueDisallowChatParticipants <pyeitaa.raw.types.PrivacyValueDisallowChatParticipants>`
            - :obj:`PrivacyValueDisallowContacts <pyeitaa.raw.types.PrivacyValueDisallowContacts>`
            - :obj:`PrivacyValueDisallowUsers <pyeitaa.raw.types.PrivacyValueDisallowUsers>`
    """

    QUALNAME = "pyeitaa.raw.base.PrivacyRule"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
