from typing import Union
from pyeitaa import raw

PassportConfig = Union[raw.types.help.PassportConfig, raw.types.help.PassportConfigNotModified]


# noinspection PyRedeclaration
class PassportConfig:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.PassportConfig <pyeitaa.raw.types.help.PassportConfig>`
            - :obj:`help.PassportConfigNotModified <pyeitaa.raw.types.help.PassportConfigNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetPassportConfig <pyeitaa.raw.functions.help.GetPassportConfig>`
    """

    QUALNAME = "pyeitaa.raw.base.help.PassportConfig"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
