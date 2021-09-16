"""VCF annotation, batch implementation

Main usage::

    with open(path_to_file, "rt") as f:
        for record in annotate_vcf_variants(f):
            ...

This file implements variant annotation as a batch operation over an
entire VCF file, using pandas to streamline the data manipulation
steps. Batch mode is appropriate where the VCF file can fit into
memory. If the file is too large, the records can be split to operate
on sections of the file at a time.
"""

import logging
from itertools import islice
from typing import Iterable, TextIO

import pandas as pd

from vcftool.vcfparse import count_header_lines, fetch_exac_bulk_variant

from .types import MISSING_VALUE, VariantRecord
from .vcfparse import most_serious_consequence, parse_field_list

logger = logging.getLogger(__name__)


def annotate_vcf_variants(vcf: TextIO) -> Iterable[VariantRecord]:
    """Generate variant records from VCF file buffer in batch

    Usage::

        with open(path_to_file, "rt") as f:
           for record in annotate_vcf_variants(f):
               print(record)
    """
    df = read_vcf(vcf)
    df = expand_variants(df)

    logger.info("Fetching ExAC metadata...")
    exac_df = fetch_exac_data(df["variant_id"])
    df = df.merge(exac_df)

    df["read_percent"] = df["ao"].astype(int) / df["ro"].astype(int) * 100
    df["read_count"] = df["ao"]

    return df[list(VariantRecord._fields)].itertuples(index=False, name="VariantRecord")


def read_vcf(vcf: TextIO) -> pd.DataFrame:
    """Read VCF records from vcf v4.1 file at `path`"""
    header_count = count_header_lines(vcf)
    vcf.seek(0)

    df = pd.read_table(
        vcf, skiprows=header_count, usecols=range(8), dtype=str, sep="\t"
    )
    df.columns = df.columns.str.lstrip("#")

    # expand INFO fields
    info_df = pd.DataFrame(df["INFO"].apply(parse_field_list).to_list())
    df = pd.concat(
        [
            df[["CHROM", "POS", "REF", "ALT", "QUAL"]],
            info_df[["TYPE", "DP", "AO", "RO"]],
        ],
        axis=1,
    )

    # split multiple alleles on a line
    df["ALT"] = df["ALT"].str.split(",")
    df["TYPE"] = df["TYPE"].str.split(",")
    df["AO"] = df["AO"].str.split(",")

    return df


def expand_variants(df: pd.DataFrame) -> pd.DataFrame:
    """Expand multi-allele VCF records so every variant has its own row"""
    rows = []
    for row in df.itertuples():
        for alt, type, ao in zip(row.ALT, row.TYPE, row.AO):
            variant_id = f"{row.CHROM}-{row.POS}-{row.REF}-{alt}"
            rows.append((variant_id, type, ao, row.RO, row.DP, row.QUAL))
    return pd.DataFrame(
        rows, columns=["variant_id", "type", "ao", "ro", "depth", "quality"]
    )


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
