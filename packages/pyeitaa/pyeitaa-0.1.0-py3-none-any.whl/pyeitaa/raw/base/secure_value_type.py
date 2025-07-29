from typing import Union
from pyeitaa import raw

SecureValueType = Union[raw.types.SecureValueTypeAddress, raw.types.SecureValueTypeBankStatement, raw.types.SecureValueTypeDriverLicense, raw.types.SecureValueTypeEmail, raw.types.SecureValueTypeIdentityCard, raw.types.SecureValueTypeInternalPassport, raw.types.SecureValueTypePassport, raw.types.SecureValueTypePassportRegistration, raw.types.SecureValueTypePersonalDetails, raw.types.SecureValueTypePhone, raw.types.SecureValueTypeRentalAgreement, raw.types.SecureValueTypeTemporaryRegistration, raw.types.SecureValueTypeUtilityBill]


# noinspection PyRedeclaration
class SecureValueType:
    """This base type has 13 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureValueTypeAddress <pyeitaa.raw.types.SecureValueTypeAddress>`
            - :obj:`SecureValueTypeBankStatement <pyeitaa.raw.types.SecureValueTypeBankStatement>`
            - :obj:`SecureValueTypeDriverLicense <pyeitaa.raw.types.SecureValueTypeDriverLicense>`
            - :obj:`SecureValueTypeEmail <pyeitaa.raw.types.SecureValueTypeEmail>`
            - :obj:`SecureValueTypeIdentityCard <pyeitaa.raw.types.SecureValueTypeIdentityCard>`
            - :obj:`SecureValueTypeInternalPassport <pyeitaa.raw.types.SecureValueTypeInternalPassport>`
            - :obj:`SecureValueTypePassport <pyeitaa.raw.types.SecureValueTypePassport>`
            - :obj:`SecureValueTypePassportRegistration <pyeitaa.raw.types.SecureValueTypePassportRegistration>`
            - :obj:`SecureValueTypePersonalDetails <pyeitaa.raw.types.SecureValueTypePersonalDetails>`
            - :obj:`SecureValueTypePhone <pyeitaa.raw.types.SecureValueTypePhone>`
            - :obj:`SecureValueTypeRentalAgreement <pyeitaa.raw.types.SecureValueTypeRentalAgreement>`
            - :obj:`SecureValueTypeTemporaryRegistration <pyeitaa.raw.types.SecureValueTypeTemporaryRegistration>`
            - :obj:`SecureValueTypeUtilityBill <pyeitaa.raw.types.SecureValueTypeUtilityBill>`
    """

    QUALNAME = "pyeitaa.raw.base.SecureValueType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
