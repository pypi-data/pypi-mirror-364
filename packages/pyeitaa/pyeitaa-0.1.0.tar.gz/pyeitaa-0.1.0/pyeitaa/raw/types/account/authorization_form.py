from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class AuthorizationForm(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.AuthorizationForm`.

    Details:
        - Layer: ``135``
        - ID: ``-0x52d1e328``

    Parameters:
        required_types: List of :obj:`SecureRequiredType <pyeitaa.raw.base.SecureRequiredType>`
        values: List of :obj:`SecureValue <pyeitaa.raw.base.SecureValue>`
        errors: List of :obj:`SecureValueError <pyeitaa.raw.base.SecureValueError>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        privacy_policy_url (optional): ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAuthorizationForm <pyeitaa.raw.functions.account.GetAuthorizationForm>`
    """

    __slots__: List[str] = ["required_types", "values", "errors", "users", "privacy_policy_url"]

    ID = -0x52d1e328
    QUALNAME = "types.account.AuthorizationForm"

    def __init__(self, *, required_types: List["raw.base.SecureRequiredType"], values: List["raw.base.SecureValue"], errors: List["raw.base.SecureValueError"], users: List["raw.base.User"], privacy_policy_url: Optional[str] = None) -> None:
        self.required_types = required_types  # Vector<SecureRequiredType>
        self.values = values  # Vector<SecureValue>
        self.errors = errors  # Vector<SecureValueError>
        self.users = users  # Vector<User>
        self.privacy_policy_url = privacy_policy_url  # flags.0?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        required_types = TLObject.read(data)
        
        values = TLObject.read(data)
        
        errors = TLObject.read(data)
        
        users = TLObject.read(data)
        
        privacy_policy_url = String.read(data) if flags & (1 << 0) else None
        return AuthorizationForm(required_types=required_types, values=values, errors=errors, users=users, privacy_policy_url=privacy_policy_url)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.privacy_policy_url is not None else 0
        data.write(Int(flags))
        
        data.write(Vector(self.required_types))
        
        data.write(Vector(self.values))
        
        data.write(Vector(self.errors))
        
        data.write(Vector(self.users))
        
        if self.privacy_policy_url is not None:
            data.write(String(self.privacy_policy_url))
        
        return data.getvalue()
