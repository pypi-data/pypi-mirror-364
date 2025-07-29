import re
from datetime import date
from typing import Union

FY_REGEX = re.compile(r"^(\d{4}) ?[\-\/] ?(\d{2,4})$")
DEFAULT_END_MONTH = 3


class FinancialYear:
    """Represents a financial year."""

    def __init__(self, fy: str, separator: str = "-") -> None:
        match = FY_REGEX.match(fy)
        if not match:
            err = "Financial year must be in the format YYYY-YY"
            raise ValueError(err)
        self.separator: str = separator

        self.year = int(match.group(1))
        self.end_year: int = self.year + 1

        self.fy = f"{self.year}{self.separator}{str(self.end_year)[-2:]}"

        self.start_date = date(self.year, 4, 1)
        self.end_date = date(self.end_year, 3, 31)

    @classmethod
    def from_int(cls, year_int: int, separator: str = "-") -> "FinancialYear":
        return cls(f"{year_int}-{str(year_int + 1)[-2:]}", separator=separator)

    @classmethod
    def from_date(cls, d: date, separator: str = "-") -> "FinancialYear":
        if d.month <= DEFAULT_END_MONTH:
            return cls.from_int(d.year - 1, separator=separator)
        return cls.from_int(d.year, separator=separator)

    def __str__(self) -> str:
        return self.fy

    def __repr__(self) -> str:
        return self.fy

    def __hash__(self) -> int:
        return hash(self.fy)

    def __lt__(self, other: Union["FinancialYear", int]) -> bool:
        if isinstance(other, int):
            return self.year < other
        return self.year < other.year

    def __le__(self, other: Union["FinancialYear", int]) -> bool:
        if isinstance(other, int):
            return self.year <= other
        return self.year <= other.year

    def __eq__(self, other) -> bool:
        if isinstance(other, int):
            return self.year == other
        return str(self) == str(other)

    def __ne__(self, other) -> bool:
        if isinstance(other, int):
            return self.year != other
        return str(self) != str(other)

    def __gt__(self, other: Union["FinancialYear", int]) -> bool:
        if isinstance(other, int):
            return self.year > other
        return self.year > other.year

    def __ge__(self, other: Union["FinancialYear", int]) -> bool:
        if isinstance(other, int):
            return self.year >= other
        return self.year >= other.year

    def __sub__(
        self, other: Union["FinancialYear", int]
    ) -> Union["FinancialYear", int]:
        if isinstance(other, int):
            return FinancialYear.from_int(self.year - other, separator=self.separator)
        return self.year - other.year

    def __add__(self, other: int) -> "FinancialYear":
        return FinancialYear.from_int(self.year + other, separator=self.separator)

    def __contains__(self, d: date) -> bool:
        if not isinstance(d, date):
            err = "FinancialYear can only contain dates"
            raise NotImplementedError(err)
        return self.start_date <= d <= self.end_date

    def __int__(self) -> int:
        return self.year

    def __float__(self) -> float:
        return float(self.year)

    def next_year(self) -> "FinancialYear":
        return FinancialYear.from_int(self.year + 1, separator=self.separator)

    def previous_year(self) -> "FinancialYear":
        return FinancialYear.from_int(self.year - 1, separator=self.separator)

    def previous_n_years(
        self, n_previous: int = 2, n_future: int = 0
    ) -> list["FinancialYear"]:
        """Returns a list of previous and future financial years."""
        return (
            [
                FinancialYear.from_int(y, separator=self.separator)
                for y in range(self.year - n_previous, self.year)
            ]
            + [self]
            + [
                FinancialYear.from_int(y, separator=self.separator)
                for y in range(self.year + 1, self.year + n_future + 1)
            ]
        )

    @staticmethod
    def range(
        fy: Union["FinancialYear", str], other: Union["FinancialYear", str]
    ) -> list["FinancialYear"]:
        """Returns a list of financial years between two financial years."""
        if isinstance(fy, str):
            fy = FinancialYear(fy)
        if isinstance(other, str):
            other = FinancialYear(other)
        if fy.year > other.year:
            return [
                FinancialYear.from_int(y, separator=fy.separator)
                for y in range(other.year, fy.year + 1)
            ]
        return [
            FinancialYear.from_int(y, separator=fy.separator)
            for y in range(fy.year, other.year + 1)
        ]
