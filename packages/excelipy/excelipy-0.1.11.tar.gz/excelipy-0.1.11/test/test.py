import logging
from pathlib import Path

import pandas as pd

import excelipy as ep


def df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "testing": [1, 2, 3],
            "tested": ["Yay", "Thanks", "Bud"],
        }
    )


def df2() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "testing": [1, 2, 3],
            "tested": [
                "Yayyyyyyyyyyyyyyyyyyyyyyyyy this is a long phrase",
                "Thanks a lot",
                "Bud",
            ],
        }
    )


def simple_example():
    sheets = [
        ep.Sheet(
            name="Hello!",
            components=[
                ep.Text(text="Hello world!", width=2),
                ep.Fill(width=2, style=ep.Style(background="#33c481")),
                ep.Table(data=df()),
            ],
            style=ep.Style(padding=1),
            grid_lines=False,
        ),
    ]

    excel = ep.Excel(
        path=Path("filename.xlsx"),
        sheets=sheets,
    )

    ep.save(excel)


def one_table():
    sheets = [
        ep.Sheet(
            name="Hello!",
            components=[
                ep.Table(data=df())
            ],
        ),
    ]

    excel = ep.Excel(
        path=Path("filename.xlsx"),
        sheets=sheets,
    )

    ep.save(excel)


def two_tables():
    sheets = [
        ep.Sheet(
            name="Hello!",
            components=[
                ep.Table(
                    data=df2(),
                    style=ep.Style(padding_bottom=1, font_size=20)
                    ),
                ep.Table(data=df()),
            ],
        ),
        ep.Sheet(
            name="Hello again!",
            components=[
                ep.Table(data=df(), style=ep.Style(padding_bottom=1)),
                ep.Table(data=df()),
            ],
        ),
    ]

    excel = ep.Excel(
        path=Path("filename.xlsx"),
        sheets=sheets,
    )

    ep.save(excel)


def simple_image():
    sheets = [
        ep.Sheet(
            name="Hello!",
            components=[
                ep.Image(
                    path=Path("resources/img.png"),
                    width=2,
                    height=5,
                    style=ep.Style(border=2),
                ),
            ],
        ),
    ]

    excel = ep.Excel(
        path=Path("filename.xlsx"),
        sheets=sheets,
    )

    ep.save(excel)


def one_table_no_grid():
    sheets = [
        ep.Sheet(
            name="Hello!",
            components=[
                ep.Table(data=df())
            ],
            grid_lines=False,
            style=ep.Style(padding=1),
        ),
    ]

    excel = ep.Excel(
        path=Path("filename.xlsx"),
        sheets=sheets,
    )

    ep.save(excel)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    two_tables()
