from typing import Union
from pyeitaa import raw

GlobalPrivacySettings = Union[raw.types.GlobalPrivacySettings]


# noinspection PyRedeclaration
class GlobalPrivacySettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`GlobalPrivacySettings <pyeitaa.raw.types.GlobalPrivacySettings>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetGlobalPrivacySettings <pyeitaa.raw.functions.account.GetGlobalPrivacySettings>`
            - :obj:`account.SetGlobalPrivacySettings <pyeitaa.raw.functions.account.SetGlobalPrivacySettings>`
    """

    QUALNAME = "pyeitaa.raw.base.GlobalPrivacySettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
