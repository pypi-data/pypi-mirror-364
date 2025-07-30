from enum import StrEnum, EnumMeta


class TcxStrEnumMeta(EnumMeta):
    # Map special string values to their Python equivalents
    SPECIAL_STRING_MAP = {
        "None": "NONE",
        "-INF": "NEGATIVE_INF",
        "False": "FALSE",
        "True": "TRUE",
    }
    SPECIAL_STRING_MAP_INV = {v: k for k, v in SPECIAL_STRING_MAP.items()}

    def __getitem__(self, name):
        name = self.SPECIAL_STRING_MAP.get(name, name)
        name = name.replace("__", ".")
        return super().__getitem__(name).value


# class TcxStrEnum(StrEnum, metaclass=TcxStrEnumMeta):
#    @staticmethod
#    def _generate_next_value_(name, start, count, last_values):
#        value = TcxStrEnumMeta.SPECIAL_STRING_MAP_INV.get(name, name)
#        return value.replace('__', '.')


class TcxStrEnum(StrEnum):

    @property
    def is_valid(self) -> bool:
        """Check if the enum member is valid."""
        return getattr(self, "_is_valid", True)

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        value = TcxStrEnumMeta.SPECIAL_STRING_MAP_INV.get(name, name)
        return value.replace("__", ".")

    def __new__(cls, value):
        # This is still fine for defined values
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj._is_valid = True  # Indicates it's a valid enum member
        return obj

    @classmethod
    def _missing_(cls, value):
        if not isinstance(value, str):
            raise ValueError(f"{value!r} is not a valid {cls.__name__}")

        # Bypass __new__ and avoid recursion by calling `str.__new__` directly
        obj = str.__new__(cls, value)
        obj._name_ = None  # Indicates it's not one of the defined enum members
        obj._value_ = value
        obj._is_valid = False  # Indicates it's not a valid enum member
        return obj
