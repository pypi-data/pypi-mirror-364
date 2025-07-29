from typing import Union
from pyeitaa import raw

Dialogs = Union[raw.types.messages.Dialogs, raw.types.messages.DialogsNotModified, raw.types.messages.DialogsSlice]


# noinspection PyRedeclaration
class Dialogs:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.Dialogs <pyeitaa.raw.types.messages.Dialogs>`
            - :obj:`messages.DialogsNotModified <pyeitaa.raw.types.messages.DialogsNotModified>`
            - :obj:`messages.DialogsSlice <pyeitaa.raw.types.messages.DialogsSlice>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDialogs <pyeitaa.raw.functions.messages.GetDialogs>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.Dialogs"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
