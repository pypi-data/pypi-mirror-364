"""Parse bank PDF statements for bank operations."""
import re
from re import Match

from .models import Operation


class SberParser:
    """Designed to parse lines from Sberbank PDF statements and
    convert them into `Operation` objects.
    """ # noqa: D205

    date_prefix = r"\d{2}\.\d{2}\.\d{4}"
    income = r"\W\+\S+\W"
    main_line = (r"(?P<date>\d{2}\.\d{2}\.\d{4})\W(?P<time>\d{2}\:\d{2})\W(\d+)\W"
                 r"(?P<category>\D+)\W(?P<sum>\S+)\W(?P<remains>\S+)")

    @staticmethod
    def _replace_nbsp(str_: str) -> str:
        """Replace non-breaking space ' ' with regular space.

        Args:
            str_: The input string that may contain non-breaking spaces.

        Returns:
            A string where all non-breaking spaces are replaced with regular spaces.

        """  # noqa: RUF002
        return str_.replace(" ", "")

    @staticmethod
    def _replace_comma(str_: str) -> str:
        """Replace comma ',' with dot '.' for float parsing.

        Args:
            str_: The input string that may contain commas as decimal separators.

        Returns:
            A string where all commas are replaced with dots.

        """
        return str_.replace(",", ".")

    @classmethod
    def is_operation(cls, str_: str) -> bool:
        """
        Use to filter strings that conform to the expected format
        of a bank transaction.

        Args:
            str_: The string to check.

        Returns:
            True if the string starts with a date in the format DD.MM.YYYY,
            otherwise False.

        Example:
            ```python
                print(cls.is_operation("12.03.2024 14:22 456789 КАФЕ +100.00 12345.67"))
                #> True
                print(cls.is_operation("Some random text without a date"))
                #> False
            ```

        """  # noqa: RUF002, D205, D212
        return bool( re.match(pattern=cls.date_prefix, string=str_))

    @classmethod
    def parse_main_line(cls, str_: str) -> Operation | None:
        """Parse a line into an Operation object if it matches the pattern.

        Args:
            str_: A line from a PDF statement that may contain information.

        Returns:
            An `Operation` object if the line matches the pattern, otherwise None.

        Example:
            ```python
                line = "12.03.2024 14:22 456789 КАФЕ +100.00 12345.67"
                parser = SberParser()
                operation = parser.parse_main_line(line)
                print(operation.date)
                #> datetime.date(2024, 3, 12)
            ```

        """ # noqa: RUF002
        operation: Operation | None = None

        str_ = cls._replace_nbsp(str_=str_)
        str_ = cls._replace_comma(str_=str_)

        if cls.is_operation(str_=str_):
            matched: Match | None = re.match(pattern=cls.main_line, string=str_)
            if matched:
                is_income = (
                    bool(re.search(pattern=cls.income, string=str_))
                )
                operation = Operation.from_match(match=matched, is_income=is_income)

        return operation

    @classmethod
    def parse_lines(cls, str_: str | list[str]) -> list:
        """Parse a list of strings or a single string into a list of Operation objects.

        Skip lines that do not match the expected format of a bank operation.

        Args:
            str_: A single string or a list of strings from a PDF statement.

        Returns:
            A list of `Operation` objects created from matching lines.

        Example:
            ```python
                lines = [
                    "12.03.2024 14:22 456789 КАФЕ +100.00 12345.67",
                    "Некорректная строка",
                    "13.03.2024 15:30 123456 МАГАЗИН -200.00 12145.67"
                ]
                parser = SberParser()
                operations = parser.parse_lines(lines)
                print(len(operations))
                #> 2
            ```

        """
        operations: list[Operation] = []

        for line in str_:
            if re.match(pattern=cls.date_prefix, string=line):
                stat = cls.parse_main_line(str_=line)
                if stat:
                    operations.append(stat)

        return operations
