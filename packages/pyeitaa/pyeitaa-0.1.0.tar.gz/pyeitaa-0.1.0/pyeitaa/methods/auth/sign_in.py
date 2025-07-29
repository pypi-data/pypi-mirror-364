import logging

import pyeitaa
from ...raw.functions.auth.sign_in import SignIn as SignIn_
from ...raw.types.auth.authorization_sign_up_required import AuthorizationSignUpRequired
from ...types import User

log = logging.getLogger(__name__)


class SignIn:
    async def sign_in(
        self: "pyeitaa.Client",
        phone_number: str,
        phone_code_hash: str,
        phone_code: str
    ) -> User:
        phone_number = phone_number.strip(" +")

        r = await self.invoke(
            SignIn_(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                phone_code=phone_code
            ),
            check_connection=False
        )

        if isinstance(r, AuthorizationSignUpRequired):
            raise NotImplementedError("The user must have already registered.")

        else:
            self.storage.token = r.token
            self.storage.user_id = r.user.id

            return User._parse(self, r.user)
