from copy import deepcopy
from datetime import date, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from src.statement_reader.models import Operation

TEST_OPERATION_DATE = {
    "date": "10.07.2025",
    "category": "Отдых и развлечения",
    "is_income": False,
    "remains": "87748.35",
    "sum": "260.00",
    "time": "15:27",
}


class TestModels:
    cls = Operation

    @pytest.mark.parametrize(
        "date_, expected_date, is_failed",
        [
            ("2025-04-05", datetime(2025, 4, 5), True),
            ("2025-04-05 14:30:00", datetime(2025, 4, 5, 14, 30), True),
            ("05.04.2025", datetime(2025, 4, 5), False),
            ("05/04/2025", datetime(2025, 4, 5), True),
            (datetime(2025, 4, 5), datetime(2025, 4, 5), False),
        ],
    )
    def test_parse_date(self, date_: Any, expected_date: date, is_failed: bool):
        data = deepcopy(TEST_OPERATION_DATE) | {"date": date_}

        if is_failed:
            with pytest.raises(ValidationError) as exc:
                self.cls(**data)
            assert exc.type is ValidationError
        else:
            operation = self.cls(**data)
            assert operation.date == expected_date.date()

    @pytest.mark.parametrize(
        "date_, expected_weekday",
        [
            ("05.04.2025", 6),
            ("06.04.2025", 7),
            ("07.04.2025", 1),
            ("08.04.2025", 2),
            ("09.04.2025", 3),
            ("10.04.2025", 4),
            ("11.04.2025", 5),
        ],
    )
    def test_weekday_property(self, date_: str, expected_weekday: int):
        data = deepcopy(TEST_OPERATION_DATE) | {"date": date_}

        operation = self.cls(**data)
        assert operation.weekday == expected_weekday
