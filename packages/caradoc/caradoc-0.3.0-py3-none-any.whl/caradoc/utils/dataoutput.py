from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Union

import pandas as pd
from xlsxwriter import Workbook  # type: ignore
from xlsxwriter.worksheet import Worksheet  # type: ignore


class ExcelTable:
    """Represents a table in an Excel workbook.

    The table itself is a pandas DataFrame. The DataFrame
    index is not written to the Excel file.

    Allows for specifying a title, summary and notes for the table.

    # Parameters

    - `df`: pandas DataFrame
    - `title`: Optional title for the table
    - `summary`: Optional summary for the table
    - `notes`: Optional notes for the table

    # Methods

    - `to_excel_table()`: Writes just the datatable (`df`) to an Excel file
        as a Table (with filters)
    - `to_excel()`: Writes the table to an Excel file as a Table, with the
        title and summary as a header and the notes as a footer."""

    def __init__(
        self,
        df: pd.DataFrame,
        title: str | None = None,
        summary: str | None = None,
        notes: str | None = None,
    ):
        self.df: pd.DataFrame = df
        self.title: str | None = title
        self.summary: str | None = summary
        self.notes: str | None = notes

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExcelTable):
            return False
        if getattr(self, "title", None) or getattr(other, "title", None):
            return getattr(self, "title", None) == getattr(other, "title", None)
        return self.df.equals(other.df)

    def __hash__(self) -> int:
        if getattr(self, "title", None):
            return hash(self.title)
        return hash(self.df.to_dict())

    def to_excel_table(
        self,
        writer: pd.ExcelWriter,
        sheet_name: str,
        column_widths: dict[str, int] | None = None,
        max_col_width: int = 50,
        startrow: int = 0,
        *,
        do_column_widths: bool = True,
        **kwargs,
    ):
        self.df.to_excel(
            writer,
            sheet_name=sheet_name,
            startrow=startrow + 1,
            header=False,
            index=False,
            **kwargs,
        )

        if column_widths is None:
            column_widths = {
                k: v
                for k, v in self.df.apply(
                    lambda x: x.astype(str).str.len().max(), axis=0
                )
                .apply(lambda x: min(x, max_col_width))
                .to_dict()
                .items()
                if isinstance(k, str) and isinstance(v, int)
            }

        # Get the xlsxwriter workbook and worksheet objects.
        if not isinstance(writer.book, Workbook):
            msg = "Expected a xlsxwriter Workbook"
            raise TypeError(msg)
        _: Workbook = writer.book
        worksheet: Worksheet = writer.sheets[sheet_name]

        # Get the dimensions of the dataframe.
        (max_row, max_col) = self.df.shape
        max_row = startrow + max_row

        # Create a list of column headers, to use in add_table().
        column_settings = [{"header": column} for column in self.df.columns]

        # Add the Excel table structure. Pandas will add the data.
        worksheet.add_table(
            startrow, 0, max_row, max_col - 1, {"columns": column_settings}
        )

        # Make the columns wider for clarity.
        if do_column_widths:
            for col_index, column in enumerate(self.df.columns):
                column_name = str(column)
                worksheet.set_column(
                    col_index,
                    col_index,
                    min(
                        max(column_widths.get(column_name, 12), len(column_name)),
                        max_col_width,
                    ),
                )

    def to_excel(
        self, writer: pd.ExcelWriter, sheet_name: str, current_row: int = 0, **kwargs
    ):
        additional_rows = 0
        to_write: list[Union[tuple[int, int, str, Any], tuple[int, int, str]]] = []  # noqa: UP007

        # write the title
        if self.title is not None:
            title_format = writer.book.add_format(  # type: ignore
                {
                    "bold": True,
                    "font_size": 15,
                }
            )
            to_write.append((current_row, 0, self.title, title_format))
            current_row += 1
            additional_rows = 1

        # write the summary
        if self.summary is not None:
            to_write.append((current_row, 0, self.summary))
            current_row += 1
            additional_rows = 1

        current_row += additional_rows

        self.to_excel_table(
            writer, sheet_name=sheet_name, startrow=current_row, **kwargs
        )
        current_row += len(self.df) + 1

        # write any notes
        if self.notes is not None:
            to_write.append((current_row, 0, self.notes))
            current_row += 1

        for args in to_write:
            writer.sheets[sheet_name].write(*args)

        return current_row + 1


class DataOutput:
    """Represents a collection of ExcelTables to be written to an Excel file.

    # Methods

    - `add_table()`: Adds a table to the DataOutput
    - `write()`: Writes the DataOutput to an Excel file"""

    def __init__(self) -> None:
        self.sheets: defaultdict[str, list[ExcelTable]] = defaultdict(lambda: [])

    def add_table(
        self,
        df: Union[pd.DataFrame, ExcelTable],  # noqa: UP007
        sheet: str,
        **kwargs,
    ) -> pd.DataFrame:
        """Adds a table to the DataOutput.

        Note that adding a dataframe with the same title as an existing table will
        overwrite the existing table.

        # Parameters

        - `df`: pandas DataFrame or ExcelTable
        - `sheet`: Name of the sheet to write the table to
        - `kwargs`: Additional arguments to pass to ExcelTable constructor.
            Only used if `df` is a DataFrame. The accepted arguments are `title`,
            `summary` and `notes` - all of which should be strings.
        """
        if isinstance(df, pd.DataFrame):
            if isinstance(df.index, pd.RangeIndex):
                et = ExcelTable(df, **kwargs)
            else:
                et = ExcelTable(df.reset_index(), **kwargs)
        else:
            et = df
        self.sheets[sheet] = [t for t in self.sheets[sheet] if t != et] + [et]
        return et.df

    def get_sheet_names(self) -> dict[str, str]:
        """Returns a dictionary of sheet names and their titles."""
        sheet_names: dict[str, str] = {}
        for sheet in self.sheets:
            sheet_name = re.sub(r"['\*/:\?\[\]\\\/]+", "", sheet)[
                :31
            ]  # Excel sheet names must be <= 31 characters
            if len(sheet_name) == 0:
                sheet_name = "Sheet"
            if sheet_name in sheet_names.values():
                # If the sheet name already exists, append a number to make it unique
                count = 1
                suffix = f"_{count:.0f}"
                truncate_length = 31 - len(suffix)
                while f"{sheet_name[:truncate_length]}{suffix}" in sheet_names.values():
                    count += 1
                    suffix = f"_{count:.0f}"
                    truncate_length = 31 - len(suffix)
                sheet_name = f"{sheet_name[:truncate_length]}{suffix}"
            sheet_names[sheet] = sheet_name
        return sheet_names

    def write(self, file_name: str) -> None:
        """Writes the DataOutput to an Excel file.

        # Parameters

        - `file_name`: Name of the file to write to"""
        sheet_names = self.get_sheet_names()
        with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
            for sheet_name, tables in self.sheets.items():
                current_row = 0
                for table in tables:
                    current_row = table.to_excel(
                        writer,
                        sheet_name=sheet_names[sheet_name],
                        current_row=current_row,
                    )
