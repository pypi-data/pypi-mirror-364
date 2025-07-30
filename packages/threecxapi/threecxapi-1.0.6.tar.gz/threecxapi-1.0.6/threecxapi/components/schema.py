from typing import Any
from enum import auto
from functools import lru_cache
from pydantic import BaseModel, PrivateAttr
from threecxapi.util import TcxStrEnum


class Schema(BaseModel):
    # Private field to track validation warnings
    _warnings: list[str] = PrivateAttr(default_factory=list)

    def add_warning(self, msg: str):
        self._warnings.append(msg)

    @property
    def warnings(self) -> list[str]:
        return self._warnings.copy()

    def model_post_init(self, __context: Any) -> None:
        for field_name, value in self.__dict__.items():
            if isinstance(value, TcxStrEnum) and not value.is_valid:
                self.add_warning(
                    f"Field '{field_name}' has unknown value '{value}', which is not a defined member of {type(value).__name__}."
                )

    def model_dump(self, **kwargs) -> dict[str, Any]:
        # Set default options for model_dump
        default_options = {
            "exclude_unset": True,
            "exclude_none": True,
            "serialize_as_any": True,
            "by_alias": True,
        }

        # Update with any user-provided options
        default_options.update(kwargs)
        # Call the original model_dump with the updated options
        return super().model_dump(**default_options)

    @classmethod
    @lru_cache
    def to_enum(cls) -> TcxStrEnum:
        """Creates an Enum based on the fields of the Schema class."""
        # Create a new TcxStrEnum
        return TcxStrEnum(cls.__name__ + "Properties", {field_name: auto() for field_name in cls.__annotations__.keys()})
