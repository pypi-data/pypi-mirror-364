"""Provides a data model from a bank export in PDF format."""
from datetime import date, datetime, time
from re import Match
from typing import Any

from pydantic import BaseModel, computed_field, field_validator


class Operation(BaseModel):
    """Represents a single bank operation parsed from a PDF statement.

    Attributes:
        date (date): The date of the operation in format 'DD.MM.YYYY'.
        time (time): The time of the operation.
        category (str): The category or type of the operation.
        sum (float): The amount of money involved in the operation.
        remains (float): The remaining balance after the operation.
        is_income (bool): Whether the operation is an income (True) or expense (False).

    """

    date: date
    time: time
    category: str
    sum: float
    remains: float
    is_income: bool = False

    @field_validator("date", mode="before")
    def parse_date(cls, v: Any) -> Any:  # noqa N805
        """Parse a string into a date object using the format 'DD.MM.YYYY'.

        Use this validator to convert a string representation of a date into a Python
        date object before model initialization.

        Args:
            v (Any): The input value to be validated and converted to a date.

        Returns:
            date: A parsed date object if input is a valid string
            in 'DD.MM.YYYY' format.

        Raises:
            ValueError: If the string is not in the correct date format.

        Example:
            ```python
                print(cls.parse_date("12.03.2024"))
                #> datetime.date(2024, 3, 12)
                print(cls.parse_date("invalid-date"))
                #> Traceback (most recent call last):
                #>   ...
                #> ValueError: time data 'invalid-date' does not match format '%d.%m.%Y'
            ```

        """
        if isinstance(v, str):
            return datetime.strptime(v, "%d.%m.%Y").date() #noqa DTZ007
        return v

    @computed_field
    @property
    def weekday(self) -> int:
        """Return the ISO weekday number for the operation's date.

        Use this property to determine the day of the week according to the ISO standard,
        where Monday is 1 and Sunday is 7.

        Returns:
            int: An integer between 1 (Monday) and 7 (Sunday) representing the weekday.

        Example:
            ```python
                from datetime import date
                op = Operation(date=date(2024, 3, 12), time="14:22", category="Coffee", sum=100.0, remains=12345.67)
                print(op.weekday)
                #> 2  # Tuesday
            ```

        """ # noqa E501
        return self.date.isoweekday()

    @classmethod
    def from_match(cls, match: Match, *, is_income: bool = False) -> "Operation":
        r"""Create an Operation instance from a regex match object.

        Use this class method to construct an Operation object from a regular
        expression match with named groups.

        Args:
            match: A regex match object with named groups 'date', 'time', 'category', 'sum', 'remains'.
            is_income: Whether the operation is income (True) or expense (False). Defaults to False.

        Returns:
            An initialized Operation instance populated with values from the match.

        Example:
            ```python
                import re
                line = "12.03.2024 14:22 456789 КАФЕ +100.00 12345.67"
                pattern = r"(?P<date>\d{2}\.\d{2}\.\d{4})\W(?P<time>\d{2}\:\d{2})\W(\d+)\W(?P<category>\D+)\W(?P<sum>\S+)\W(?P<remains>\S+)"
                match = re.match(pattern, line)
                operation = Operation.from_match(match=match, is_income=True)
                print(operation.sum)
                #> 100.0
            ```

        """ # noqa E501, RUF002
        date_ = match.group("date")
        return cls(
            date=date_,
            time=match.group("time"),
            category=match.group("category"),
            sum=match.group("sum"),
            remains=match.group("remains"),
            is_income=is_income,
        )
