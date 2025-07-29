import tempfile

import pandas as pd

from caradoc import DataOutput, ExcelTable


def test_dataoutput():
    do = DataOutput()
    df = pd.DataFrame({"a": [1, 2, 3]})
    do.add_table(df, "test", title="test")
    assert do.sheets["test"][0].df.equals(df)


def test_dataoutput_exceltable():
    do = DataOutput()
    df = pd.DataFrame({"a": [1, 2, 3]})
    tb = ExcelTable(df, title="test")
    do.add_table(tb, "test")
    assert do.sheets["test"][0].df.equals(df)


def test_dataoutput_excel():
    do = DataOutput()
    df = pd.DataFrame({"a": [1, 2, 3]})
    do.add_table(df, "test", title="test")
    with tempfile.TemporaryDirectory() as tmp:
        do.write(tmp + "/test.xlsx")
        assert pd.read_excel(tmp + "/test.xlsx", sheet_name="test", skiprows=2).equals(df)


def test_dataoutput_duplicate():
    do = DataOutput()
    df = pd.DataFrame({"a": [1, 2, 3]})
    do.add_table(df, "test", title="test")
    do.add_table(df, "test", title="test")
    assert len(do.sheets["test"]) == 1

    do.add_table(df, "test", title="test_again")
    assert len(do.sheets["test"]) == 2


def test_dataoutput_duplicate_df():
    do = DataOutput()
    df = pd.DataFrame({"a": [1, 2, 3]})
    do.add_table(df, "test")
    do.add_table(df, "test")
    assert len(do.sheets["test"]) == 1

    do.add_table(df, "test", title="test_again")
    assert len(do.sheets["test"]) == 2


def test_dataoutput_excel_true_index():
    do = DataOutput()
    df = pd.DataFrame({"a": [1, 2, 3]}, index=["A", "B", "C"])
    do.add_table(df, "test", title="test")
    with tempfile.TemporaryDirectory() as tmp:
        do.write(tmp + "/test.xlsx")
        assert pd.read_excel(tmp + "/test.xlsx", sheet_name="test", skiprows=2).equals(df.reset_index())


def test_dataoutput_excel_column_widths():
    df = pd.DataFrame({"a": [1, 2, 3]})
    et = ExcelTable(df, title="test")
    with tempfile.TemporaryDirectory() as tmp:
        with pd.ExcelWriter(tmp + "/test.xlsx") as writer:
            et.to_excel_table(writer, sheet_name="test", column_widths={"a": 10})

        with pd.ExcelWriter(tmp + "/test2.xlsx") as writer:
            et.to_excel_table(writer, sheet_name="test", do_column_widths=False)


def test_dataoutput_excel_no_title():
    df = pd.DataFrame({"a": [1, 2, 3]})
    et = ExcelTable(df)
    with tempfile.TemporaryDirectory() as tmp:
        with pd.ExcelWriter(tmp + "/test.xlsx") as writer:
            et.to_excel(writer, sheet_name="test")


def test_dataoutput_excel_summary_notes():
    do = DataOutput()
    df = pd.DataFrame({"a": [1, 2, 3]})
    do.add_table(df, "test", title="test", summary="summary", notes="notes")
    with tempfile.TemporaryDirectory() as tmp:
        do.write(tmp + "/test.xlsx")
        # length should be:
        # 1 row for title
        # 1 row for summary
        # 1 row gap
        # 4 rows for data
        # 1 row for notes
        # = 8
        assert len(pd.read_excel(tmp + "/test.xlsx", sheet_name="test", header=None)) == 8


def test_dataoutput_excel_summary_notes_double():
    do = DataOutput()
    df = pd.DataFrame({"a": [1, 2, 3]})
    do.add_table(df, "test", title="test", summary="summary", notes="notes")
    do.add_table(df, "test", title="test_again", summary="summary", notes="notes")
    with tempfile.TemporaryDirectory() as tmp:
        do.write(tmp + "/test.xlsx")
        # length should be:
        # 1 row for title
        # 1 row for summary
        # 1 row gap
        # 4 rows for data
        # 1 row for notes
        # x2 for second table
        # 1 row gap between tables
        # = 17
        assert len(pd.read_excel(tmp + "/test.xlsx", sheet_name="test", header=None)) == 17


def test_dataoutput_summary_notes():
    do = DataOutput()
    df = pd.DataFrame({"a": [1, 2, 3]})
    do.add_table(df, "test", title="test", summary="summary", notes="notes")
    assert do.sheets["test"][0].df.equals(df)


def test_exceltable_not_equal():
    df = pd.DataFrame({"a": [1, 2, 3]})
    et = ExcelTable(df, title="test")
    assert et != 1
