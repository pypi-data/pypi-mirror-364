from enum import auto, StrEnum
from threecxapi.util import TcxStrEnum, TcxStrEnumMeta


class TestTcxStrEnum:
    def test_tcxstreenummeta(self):
        assert TcxStrEnumMeta.SPECIAL_STRING_MAP["None"] == "NONE"
        assert TcxStrEnumMeta.SPECIAL_STRING_MAP_INV["NONE"] == "None"

    def test_tcxstrenum_inherits_strenum(self):
        assert issubclass(TcxStrEnum, StrEnum)

    def test_tcxstream_metaclass_is_tcxstrenummeta(self):
        assert type(TcxStrEnum) is TcxStrEnumMeta

    def test_tcxstrenum_sets_none(self):
        class test_enum(TcxStrEnum):
            NONE = auto()
            a = auto()
            b = auto()

        assert test_enum["NONE"] == "None"
        assert test_enum["None"] == "None"
