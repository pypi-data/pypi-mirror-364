from enum import Enum


class AutoName(Enum):
    def _generate_next_value_(self, *_):
        return self.lower()

    def __repr__(self):
        return f"pyeitaa.enums.{self}"