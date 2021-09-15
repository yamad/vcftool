import logging
from itertools import islice
from os import PathLike
from typing import Iterable

import pandas as pd

from vcftool.vcfparse import count_header_lines, fetch_exac_bulk_variant

from .types import MISSING_VALUE
from .vcfparse import most_serious_consequence, parse_field_list

logger = logging.getLogger(__name__)


def read_vcf(path: PathLike) -> pd.DataFrame:
    """Read VCF records from vcf v4.1 file at `path`"""
    with open(path, "rt") as f:
        header_count = count_header_lines(f)

    df = pd.read_table(path, skiprows=header_count, sep="\t")
    df.columns = df.columns.str.lstrip("#")

    # expand INFO fields
    info_df = pd.DataFrame(df["INFO"].apply(parse_field_list).to_list())
    df = pd.concat(
        [df[["CHROM", "POS", "REF", "ALT"]], info_df[["TYPE", "DP", "AO", "RO"]]],
        axis=1,
    )

    # split multiple alleles on a line
    df["ALT"] = df["ALT"].str.split(",")
    df["TYPE"] = df["TYPE"].str.split(",")
    df["AO"] = df["AO"].str.split(",")

    return df


def expand_variants(df) -> pd.DataFrame:
    long = []
    for row in df.itertuples():
        for alt, type, ao in zip(row.ALT, row.TYPE, row.AO):
            variant_id = f"{row.CHROM}-{row.POS}-{row.REF}-{alt}"
            long.append((variant_id, type, ao, row.RO, row.DP))
    return pd.DataFrame(long, columns=["variant_id", "type", "ao", "ro", "dp"])


def fetch_exac_data(variant_ids):
    """Extract consequence and allele frequency for each variant_id using ExAC API calls"""
    exac_data = []

    # presume ExAC doesn't want us downloading ~10e3 records at once, so do batches of 500
    for ids in chunked(variant_ids, 500):
        for variant_id, record in fetch_exac_bulk_variant(ids).items():
            cons = most_serious_consequence(
                record.get("consequence", {}), MISSING_VALUE
            )
            exac_frequency = record.get("variant", {}).get("allele_freq", MISSING_VALUE)

            exac_data.append((variant_id, cons, exac_frequency))
    return pd.DataFrame(
        exac_data, columns=["variant_id", "consequence", "exac_frequency"]
    )


def chunked(iterable: Iterable, n: int):
    """Return tuple chunks of size `n` from `iterable`"""
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, n))
        if chunk:
            yield chunk
        else:
            return


def main(path):
    df = read_vcf(path)
    df = expand_variants(df)

    logger.info("Fetching ExAC metadata...")
    exac_df = fetch_exac_data(df["variant_id"])
    df = df.merge(exac_df)
    return df
