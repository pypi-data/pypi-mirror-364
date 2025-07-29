from typing import Match, Self
from datetime import datetime
from enum import Enum
from json import dumps

import pyeitaa


class Object:
    def __init__(self, client: "pyeitaa.Client" = None):
        self._client = client

    def bind(self, client: "pyeitaa.Client"):
        self._client = client

        for i in self.__dict__:
            o = getattr(self, i)

            if isinstance(o, Object):
                o.bind(client)

    @staticmethod
    def default(obj: Self):
        match obj:
            case bytes():
                return repr(obj)

            case Match():
                return repr(obj)

            case Enum():
                return str(obj)

            case datetime():
                return str(obj)

        filtered_attributes = {
            attr: attr_value
            for attr, attr_value in filter(
                lambda x: not x[0].startswith("_") and x[0] != "",
                obj.__dict__.items(),
            )
            if attr_value is not None
        }

        return {
            "_": obj.__class__.__name__,
            **filtered_attributes
        }

    def __str__(self) -> str:
        return dumps(self, indent=4, default=Object.default, ensure_ascii=False)

    def __repr__(self) -> str:
        return "pyeitaa.types.{}({})".format(
            self.__class__.__name__,
            ", ".join(
                f"{attr}={repr(attr_value)}"
                for attr, attr_value in filter(lambda x: not x[0].startswith("_"), self.__dict__.items())
                if attr_value is not None
            )
        )

    def __eq__(self, other: Self) -> bool:
        for attr in self.__dict__:
            try:
                if attr.startswith("_"):
                    continue

                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                return False

        return True

    def __setstate__(self, state):
        for attr in state:
            obj = state[attr]

            if isinstance(obj, tuple) and len(obj) == 2 and obj[0] == "dt":
                state[attr] = datetime.fromtimestamp(obj[1])

        self.__dict__ = state

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_client", None)

        for attr in state:
            obj = state[attr]

            if isinstance(obj, datetime):
                state[attr] = ("dt", obj.timestamp())

        return state
