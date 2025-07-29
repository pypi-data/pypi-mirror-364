import asyncio
import logging
import platform
import re
import sys
from base36 import dumps as b36
from time import time
from io import StringIO, BytesIO
from mimetypes import MimeTypes
from pathlib import Path
from typing import Union, List, Optional

from pyeitaa import __version__
from pyeitaa import enums
from pyeitaa import raw
from pyeitaa import utils
from pyeitaa.methods import Methods
from pyeitaa.storage import Storage, FileStorage
from pyeitaa.types import User
from pyeitaa.utils import ainput
from .errors import BadRequest, SessionPasswordNeeded
from .connection import Transporter
from .mime_types import mime_types
from .session_internals import MsgId

log = logging.getLogger(__name__)


class Client(Methods):
    """Pyeitaa Client, the main means for interacting with Eitaa.

    Parameters:
        name (``str``):
            A name for the client, e.g.: "my_account".

        api_id (``int`` | ``str``, *optional*):
            The *api_id* part of the Eitaa API key, as integer or string.
            E.g.: 12345 or "12345".

        api_hash (``str``, *optional*):
            The *api_hash* part of the Eitaa API key, as string.
            E.g.: "0123456789abcdef0123456789abcdef".

        app_version (``str``, *optional*):
            Application version.
            Defaults to "Pyeitaa x.y.z".

        device_model (``str``, *optional*):
            Device model.
            Defaults to *platform.python_implementation() + " " + platform.python_version()*.

        system_version (``str``, *optional*):
            Operating System version.
            Defaults to *platform.system() + " " + platform.release()*.

        lang_pack (``str``, *optional*):
            Name of the language pack used on the client.
            Defaults to "" (empty string).

        lang_code (``str``, *optional*):
            Code of the language used on the client, in ISO 639-1 standard.
            Defaults to "en".

        system_lang_code (``str``, *optional*):
            Code of the language used on the system, in ISO 639-1 standard.
            Defaults to "en".

        session_string (``str``, *optional*):
            Pass a session string to load the session in-memory.
            Implies ``in_memory=True``.

        in_memory (``bool``, *optional*):
            Pass True to start an in-memory session that will be discarded as soon as the client stops.
            In order to reconnect again using an in-memory session without having to login again, you can use
            :meth:`~pyeitaa.Client.export_session_string` before stopping the client to get a session string you can
            pass to the ``session_string`` parameter.
            Defaults to False.

        phone_number (``str``, *optional*):
            Pass the phone number as string (with the Country Code prefix included) to avoid entering it manually.
            Only applicable for new sessions.

        phone_code (``str``, *optional*):
            Pass the phone code as string (for test numbers only) to avoid entering it manually.
            Only applicable for new sessions.

        password (``str``, *optional*):
            Pass the Two-Step Verification password as string (if required) to avoid entering it manually.
            Only applicable for new sessions.

        workdir (``str``, *optional*):
            Define a custom working directory.
            The working directory is the location in the filesystem where Pyeitaa will store the session files.
            Defaults to the parent directory of the main script.

        parse_mode (:obj:`~pyeitaa.enums.ParseMode`, *optional*):
            Set the global parse mode of the client. By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        hide_password (``bool``, *optional*):
            Pass True to hide the password when typing it during the login.
            Defaults to False, because ``getpass`` (the library used) is known to be problematic in some
            terminal environments.

        storage_engine (:obj:`~pyeitaa.storage.Storage`, *optional*):
            Pass an instance of your own implementation of session storage engine.
            Useful when you want to store your session in databases like Mongo, Redis, etc.

        loop (:py:class:`asyncio.AbstractEventLoop`, *optional*):
            Event loop.
    """

    APP_VERSION = f"Pyeitaa {__version__}"
    DEVICE_MODEL = f"{platform.python_implementation()} {platform.python_version()}"
    SYSTEM_VERSION = f"{platform.system()} {platform.release()}"

    LANG_PACK = ""
    LANG_CODE = "fa"
    SYSTEM_LANG_CODE = "fa"

    PARENT_DIR = Path(sys.argv[0]).parent

    INVITE_LINK_RE = re.compile(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:joinchat/|\+))([\w-]+)$")
    WORKDIR = PARENT_DIR

    mimetypes = MimeTypes()
    mimetypes.readfp(StringIO(mime_types))

    WEBK_API_ID = 94575
    WEBK_API_HASH = "a3406de8d171bb422bb6ddf3bbd800e2"

    def __init__(
        self,
        name: str,
        api_id: Optional[int] = WEBK_API_ID,
        api_hash: Optional[str] = WEBK_API_HASH,
        app_version: str = APP_VERSION,
        device_model: str = DEVICE_MODEL,
        system_version: str = SYSTEM_VERSION,
        lang_pack: str = LANG_PACK,
        lang_code: str = LANG_CODE,
        system_lang_code: str = SYSTEM_LANG_CODE,
        phone_number: Optional[str] = None,
        phone_code: Optional[str] = None,
        password: Optional[str] = None,
        workdir: Union[str, Path] = WORKDIR,
        parse_mode: enums.ParseMode = enums.ParseMode.DEFAULT,
        hide_password: Optional[bool] = False,
        storage_engine: Optional[Storage] = None,
        transporter: Optional[Transporter] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        super().__init__()

        self.name = name
        self.api_id = api_id
        self.api_hash = api_hash
        self.app_version = app_version
        self.device_model = device_model
        self.system_version = system_version
        self.lang_pack = lang_pack.lower()
        self.lang_code = lang_code.lower()
        self.system_lang_code = system_lang_code.lower()
        self.phone_number = phone_number
        self.phone_code = phone_code
        self.password = password
        self.workdir = Path(workdir)
        self.parse_mode = parse_mode
        self.hide_password = hide_password

        if isinstance(storage_engine, Storage):
            self.storage = storage_engine

        else:
            self.storage = FileStorage(self.name, self.workdir)

        if isinstance(transporter, Transporter):
            self.transporter = transporter

        else:
            self.transporter = Transporter()

        self.rnd_id = MsgId

        # self.parser: Parser = Parser(self) # XXX wtite the parser

        self.is_initialized = None

        self.me: Optional[User] = None

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop

        else:
            self.loop = asyncio.get_event_loop()

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *_):
        await self.stop()

    async def authorize(self) -> User:
        print(f"Welcome to Pyeitaa")
        print(f"Pyeitaa is free software and comes with ABSOLUTELY NO WARRANTY, written by MSDanesh")

        while True:
            try:
                if not self.phone_number:
                    while True:
                        value = await ainput("Enter phone number: ", loop=self.loop)

                        if not value:
                            continue

                        confirm = await ainput(f'Is "{value}" correct? (y/N): ', loop=self.loop)

                        if confirm.lower() == "y":
                            break

                    self.phone_number = value

                sent_code = await self.send_code(self.phone_number)

            except BadRequest as e:
                print(e.MESSAGE)

                self.phone_number = None
                self.bot_token = None

            else:
                break

        print(
            "The confirmation code has been sent via {}".format(
                "Eitaa app" if sent_code.type == enums.SentCodeType.APP else
                "SMS" if sent_code.type == enums.SentCodeType.SMS else
                "phone call" if sent_code.type == enums.SentCodeType.CALL else
                "phone flash call" if sent_code.type == enums.SentCodeType.FLASH_CALL else
                "unknown way"
            )
        )

        while True:
            if not self.phone_code:
                self.phone_code = await ainput("Enter confirmation code: ", loop=self.loop)

            try:
                signed_in = await self.sign_in(self.phone_number, sent_code.phone_code_hash, self.phone_code)

            except BadRequest as e:
                print(e.MESSAGE)

                self.phone_code = None

            except SessionPasswordNeeded as e:
                print(e.MESSAGE)

                while True:
                    if not self.password:
                        self.password = await ainput("Enter password: ", hide=self.hide_password, loop=self.loop)

                    try:
                        return await self.check_password(self.password) # XXX

                    except BadRequest as e:
                        print(e.MESSAGE)

                        self.password = None

            else:
                break

        return signed_in

    async def fetch_peers(self, peers: List[Union[raw.types.User, raw.types.Chat, raw.types.Channel]]) -> bool:
        is_min = False
        parsed_peers = []
        parsed_usernames = []

        for peer in peers:
            if getattr(peer, "min", False):
                is_min = True
                continue

            usernames = []
            phone_number = None

            if isinstance(peer, raw.types.User):
                peer_id = peer.id
                access_hash = peer.access_hash
                phone_number = peer.phone
                peer_type = "bot" if peer.bot else "user"

                if peer.username:
                    usernames.append(peer.username.lower())
                elif peer.usernames:
                    usernames.extend(username.username.lower() for username in peer.usernames)
            elif isinstance(peer, (raw.types.Chat, raw.types.ChatForbidden)):
                peer_id = -peer.id
                access_hash = 0
                peer_type = "group"
            elif isinstance(peer, raw.types.Channel):
                peer_id = utils.get_channel_id(peer.id)
                access_hash = peer.access_hash
                peer_type = "channel" if peer.broadcast else "supergroup"

                if peer.username:
                    usernames.append(peer.username.lower())
                elif peer.usernames:
                    usernames.extend(username.username.lower() for username in peer.usernames)
            elif isinstance(peer, raw.types.ChannelForbidden):
                peer_id = utils.get_channel_id(peer.id)
                access_hash = peer.access_hash
                peer_type = "channel" if peer.broadcast else "supergroup"
            else:
                continue

            parsed_peers.append((peer_id, access_hash, peer_type, phone_number))
            parsed_usernames.append((peer_id, usernames))

        await self.storage.update_peers(parsed_peers)
        await self.storage.update_usernames(parsed_usernames)

        return is_min

    async def load_session(self):
        await self.storage.open()

        session_empty = not all(self.storage.get_full_session())

        if session_empty:
            if not self.api_id or not self.api_hash:
                raise AttributeError("The API key is required for new authorizations.")

            now = time()

            self.storage.token = ""
            self.storage.date = int(now)
            self.storage.imei = b36(int(now % 9e65)) + b36(int(now % 9e10)) + "__web"
            self.storage.user_id = None

    def guess_mime_type(self, filename: Union[str, BytesIO]) -> Optional[str]:
        if isinstance(filename, BytesIO):
            return self.mimetypes.guess_type(filename.name)[0]

        return self.mimetypes.guess_type(filename)[0]

    def guess_extension(self, mime_type: str) -> Optional[str]:
        return self.mimetypes.guess_extension(mime_type)


class Cache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.store = {}

    def __getitem__(self, key):
        return self.store.get(key, None)

    def __setitem__(self, key, value):
        if key in self.store:
            del self.store[key]

        self.store[key] = value

        if len(self.store) > self.capacity:
            for _ in range(self.capacity // 2 + 1):
                del self.store[next(iter(self.store))]
