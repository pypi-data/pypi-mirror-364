from datetime import date

import pytest

from caradoc import FinancialYear


def test_financialyear_from_int():
    fy = FinancialYear.from_int(2020)
    assert fy == "2020-21"


def test_financialyear_from_date():
    fy = FinancialYear.from_date(date(2020, 1, 1))
    assert fy == "2019-20"

    fy = FinancialYear.from_date(date(2020, 4, 1))
    assert fy == "2020-21"


def test_financialyear_str():
    assert str(FinancialYear("2020-21")) == "2020-21"


def test_financialyear_repr():
    assert repr(FinancialYear("2020-21")) == "2020-21"


def test_financialyear_error():
    with pytest.raises(ValueError):
        FinancialYear("FLAM-FLIM")


def test_financialyear_equality():
    assert FinancialYear("2020-21") < FinancialYear("2021-22")
    assert FinancialYear("2020-21") <= FinancialYear("2021-22")
    assert FinancialYear("2020-21") <= FinancialYear("2020-21")
    assert FinancialYear("2020-21") == FinancialYear("2020-21")
    assert FinancialYear("2020-21") != FinancialYear("2021-22")
    assert FinancialYear("2020-21") >= FinancialYear("2020-21")
    assert FinancialYear("2025-26") >= FinancialYear("2020-21")
    assert FinancialYear("2025-26") > FinancialYear("2020-21")


def test_financialyear_equality_int():
    assert FinancialYear("2020-21") < 2021
    assert FinancialYear("2020-21") <= 2021
    assert FinancialYear("2020-21") <= 2020
    assert FinancialYear("2020-21") == 2020
    assert FinancialYear("2020-21") != 2021
    assert FinancialYear("2020-21") >= 2020
    assert FinancialYear("2025-26") >= 2020
    assert FinancialYear("2025-26") > 2020


def test_financialyear_addition():
    assert FinancialYear("2020-21") - FinancialYear("2019-20") == 1
    assert FinancialYear("2020-21") - 1 == FinancialYear("2019-20")
    assert FinancialYear("2020-21") + 1 == FinancialYear("2021-22")
    assert FinancialYear("2020-21") + 5 == FinancialYear("2025-26")


def test_financialyear_in_dict():
    fy = FinancialYear("2020-21")
    d = {fy: 1}
    assert d[fy] == 1


def test_financialyear_range():
    assert list(FinancialYear.range("2019-20", "2021-22")) == [
        FinancialYear("2019-20"),
        FinancialYear("2020-21"),
        FinancialYear("2021-22"),
    ]


def test_financialyear_range_backwards():
    assert list(FinancialYear.range("2021-22", "2019-20")) == [
        FinancialYear("2019-20"),
        FinancialYear("2020-21"),
        FinancialYear("2021-22"),
    ]


def test_financialyear_range_fy():
    assert list(FinancialYear.range(FinancialYear("2019-20"), FinancialYear("2021-22"))) == [
        FinancialYear("2019-20"),
        FinancialYear("2020-21"),
        FinancialYear("2021-22"),
    ]
    assert FinancialYear("2020-21") in FinancialYear.range("2019-20", "2021-22")


def test_financialyear_next_year():
    assert FinancialYear("2020-21").next_year() == FinancialYear("2021-22")


def test_financialyear_previous_year():
    assert FinancialYear("2020-21").previous_year() == FinancialYear("2019-20")


def test_financialyear_previous_n_years():
    assert FinancialYear("2020-21").previous_n_years() == [
        FinancialYear("2018-19"),
        FinancialYear("2019-20"),
        FinancialYear("2020-21"),
    ]
    assert FinancialYear("2020-21").previous_n_years(n_previous=1) == [
        FinancialYear("2019-20"),
        FinancialYear("2020-21"),
    ]
    assert FinancialYear("2020-21").previous_n_years(n_future=1) == [
        FinancialYear("2018-19"),
        FinancialYear("2019-20"),
        FinancialYear("2020-21"),
        FinancialYear("2021-22"),
    ]
    assert FinancialYear("2020-21").previous_n_years(n_previous=1, n_future=1) == [
        FinancialYear("2019-20"),
        FinancialYear("2020-21"),
        FinancialYear("2021-22"),
    ]


def test_financialyear_contains():
    d = date(2020, 4, 1)
    assert d in FinancialYear("2020-21")
    assert d not in FinancialYear("2019-20")
    assert d not in FinancialYear("2019-20")


def test_financialyear_contains_error():
    with pytest.raises(NotImplementedError):
        assert "Hello" in FinancialYear("2020-21")  # type: ignore


def test_financialyear_int():
    assert int(FinancialYear("2020-21")) == 2020
    assert int(FinancialYear("2019-20")) == 2019
    assert int(FinancialYear("2018-19")) == 2018


def test_financialyear_float():
    assert float(FinancialYear("2020-21")) == 2020.0
    assert float(FinancialYear("2019-20")) == 2019.0
    assert float(FinancialYear("2018-19")) == 2018.0
