from typing import Union
from pyeitaa import raw

InputPrivacyRule = Union[raw.types.InputPrivacyValueAllowAll, raw.types.InputPrivacyValueAllowChatParticipants, raw.types.InputPrivacyValueAllowContacts, raw.types.InputPrivacyValueAllowUsers, raw.types.InputPrivacyValueDisallowAll, raw.types.InputPrivacyValueDisallowChatParticipants, raw.types.InputPrivacyValueDisallowContacts, raw.types.InputPrivacyValueDisallowUsers]


# noinspection PyRedeclaration
class InputPrivacyRule:
    """This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputPrivacyValueAllowAll <pyeitaa.raw.types.InputPrivacyValueAllowAll>`
            - :obj:`InputPrivacyValueAllowChatParticipants <pyeitaa.raw.types.InputPrivacyValueAllowChatParticipants>`
            - :obj:`InputPrivacyValueAllowContacts <pyeitaa.raw.types.InputPrivacyValueAllowContacts>`
            - :obj:`InputPrivacyValueAllowUsers <pyeitaa.raw.types.InputPrivacyValueAllowUsers>`
            - :obj:`InputPrivacyValueDisallowAll <pyeitaa.raw.types.InputPrivacyValueDisallowAll>`
            - :obj:`InputPrivacyValueDisallowChatParticipants <pyeitaa.raw.types.InputPrivacyValueDisallowChatParticipants>`
            - :obj:`InputPrivacyValueDisallowContacts <pyeitaa.raw.types.InputPrivacyValueDisallowContacts>`
            - :obj:`InputPrivacyValueDisallowUsers <pyeitaa.raw.types.InputPrivacyValueDisallowUsers>`
    """

    QUALNAME = "pyeitaa.raw.base.InputPrivacyRule"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
