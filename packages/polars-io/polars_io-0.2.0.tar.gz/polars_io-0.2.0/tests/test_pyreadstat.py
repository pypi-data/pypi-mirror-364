from pathlib import Path
from collections.abc import Callable

import requests
import lxml.html
from tqdm import tqdm
import pandas as pd
import polars as pl
from polars.testing import assert_frame_equal


import polars_io


def _get_data(*, url: str, data: Path, suffix: str):
    with requests.get(url) as r:
        tree = lxml.html.fromstring(r.text, base_url=url)

    tree.make_links_absolute()

    sas_files = [link for link in tree.xpath("//a/@href") if link.endswith(suffix)]

    data.mkdir(parents=True, exist_ok=True)

    for f in tqdm(sas_files, desc="Getting SAS test files"):
        save_to: Path = data / f.rsplit("/", 1)[-1]

        with requests.get(f) as r:
            save_to.write_bytes(r.content)


def _test_reader(
    data: Path,
    url: str,
    suffix: str,
    correct_reader: Callable[[Path], pd.DataFrame],
    our_reader: Callable[[Path], pl.DataFrame],
):
    if not data.exists():
        print(f"Getting {suffix} files from {url}")
        _get_data(url=url, data=data, suffix=suffix)

    for file in data.glob("*.sas7bdat"):
        pandas = (
            correct_reader(file)
            .pipe(pl.from_pandas)  # type: ignore
            # make sure that binary/null columns read the same as in pyreadstat
            .with_columns(pl.col(pl.Binary, pl.Null).cast(str).fill_null(""))
        )
        ours = our_reader(file)

        try:
            assert_frame_equal(pandas, ours, check_dtypes=False)  # type: ignore
        except:
            print(pandas)
            print(ours)
            raise


def test_sas():
    _test_reader(
        data=Path("./data/sas"),
        url="https://www.alanelliott.com/sased2/ED2_FILES.html",
        suffix="sas7bdat",
        correct_reader=lambda p: pd.read_sas(p, iterator=False),  # type: ignore
        our_reader=polars_io.read_sas,
    )


def test_stata():
    _test_reader(
        data=Path("./data/stata"),
        url="https://principlesofeconometrics.com/stata.htm",
        suffix="dta",
        correct_reader=lambda p: pd.read_stata(p, iterator=False),  # type: ignore
        our_reader=polars_io.read_stata,
    )
