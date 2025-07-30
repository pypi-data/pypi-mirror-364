import pytest

from src.statement_reader.models import Operation
from src.statement_reader.parsers import SberParser


class TestParser:
    cls = SberParser

    @pytest.mark.parametrize(
        "input_str, is_operation",
        [
            (
                "10.07.2025 NASTOYASHHAYA PEKARNYA Oryol RUS. Операция по карте ****1683",
                True,
            ),
            ("Продолжение на следующей странице", False),
        ],
    )
    def test_is_operation(self, input_str: str, is_operation: bool):
        assert self.cls.is_operation(str_=input_str) is is_operation

    @pytest.mark.parametrize(
        "input_str, expected_result",
        [
            (
                "08.07.2025 18:44 928463 Оплата по QR–коду СБП 200,00 100 463,88",
                "08.07.2025 18:44 928463 Оплата по QR–коду СБП 200,00 100463,88",
            ),
            ( # noqa PT014
                "08.07.2025 18:44 928463 Оплата по QR–коду СБП 200,00 100\xa0463,88",
                "08.07.2025 18:44 928463 Оплата по QR–коду СБП 200,00 100463,88",
            ),
        ],
    )
    def test_replace_nbsp(self, input_str: str, expected_result: str):
        assert self.cls._replace_nbsp(str_=input_str) == expected_result

    @pytest.mark.parametrize(
        "input_str, expected_result",
        [
            (
                "08.07.2025 18:44 928463 Оплата по QR–коду СБП 200,00 100463,88",
                "08.07.2025 18:44 928463 Оплата по QR–коду СБП 200.00 100463.88",
            ),
        ],
    )
    def test_replace_comma(self, input_str: str, expected_result: str):
        assert self.cls._replace_comma(str_=input_str) == expected_result

    @pytest.mark.parametrize(
        "str_, expected_stat",
        [
            (
                "10.07.2025 15:27 437189 Отдых и развлечения 260,00 87748,35",
                Operation(
                    date="10.07.2025",
                    category="Отдых и развлечения",
                    is_income=False,
                    remains="87748.35",
                    sum="260.00",
                    time="15:27",
                    weekday=4,
                ),
            ),
            ("10.07.2025 YANDEX.TAXI MOSCOW RUS. Операция по карте ****1683", None),
            (
                "10.07.2025 16:00 427391 Рестораны и кафе +1240,00 88008,35",
                Operation(
                    date="10.07.2025",
                    category="Рестораны и кафе ",
                    is_income=True,
                    remains="88008.35",
                    sum="1240.00",
                    time="16:00",
                    weekday=4,
                ),
            ),
            ("10.07.2025 DIRTY BOOTS. Oryol RUS. Операция по карте ****1683", None),
        ],
    )
    def test_parse_main_line(self, str_: str, expected_stat: dict):
        assert self.cls.parse_main_line(str_=str_) == expected_stat

    @pytest.mark.parametrize(
        "str_, expected_operations",
        [
            (
                [
                    "10.07.2025 15:27 437189 Отдых и развлечения 260,00 87748,35",
                    "10.07.2025 YANDEX.TAXI MOSCOW RUS. Операция по карте ****1683",
                ],
                [
                    Operation(
                        date="10.07.2025",
                        category="Отдых и развлечения",
                        is_income=False,
                        remains="87748.35",
                        sum="260.00",
                        time="15:27",
                        weekday=4,
                    ),
                ],
            ),
            (["10.07.2025 YANDEX.TAXI MOSCOW RUS. Операция по карте ****1683"], []),
            (
                [
                    "10.07.2025 15:27 437189 Отдых и развлечения 260,00 87748,35",
                    "10.07.2025 YANDEX.TAXI MOSCOW RUS. Операция по карте ****1683",
                    "05.05.2025 10:24 947664 Прочие операции +130 500,00 153 177,62",
                    "05.05.2025 Заработная плата.Операция по счету ** ** 1618",
                    "05.05.2025 09:42 364835 Супермаркеты 722,92 22 677,62",
                    "05.05.2025 MAGNIT MM BALLISTIKA Oryol RUS.Операция по карте ** ** 1683",
                ],
                [
                    Operation(
                        date="10.07.2025",
                        category="Отдых и развлечения",
                        is_income=False,
                        remains="87748.35",
                        sum="260.00",
                        time="15:27",
                        weekday=4,
                    ),
                    Operation(
                        category="Прочие операции ",
                        date="05.05.2025",
                        is_income=True,
                        remains="153177.62",
                        sum="130500.00",
                        time="10:24",
                        weekday=1,
                    ),
                    Operation(
                        date="05.05.2025",
                        category="Супермаркеты",
                        is_income=False,
                        remains="22677.62",
                        sum="722.92",
                        time="09:42",
                        weekday=1,
                    ),
                ],
            ),
        ],
    )
    def test_parse_lines(self, str_: str, expected_operations: dict):
        assert self.cls.parse_lines(str_=str_) == expected_operations
