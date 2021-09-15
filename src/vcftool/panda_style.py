import pandas as pd

from os import PathLike

from .vcfparse import parse_field_list

def read_vcf(path: PathLike) -> pd.DataFrame:
    """Read VCF records from vcf v4.1 file at `path`"""
    with open(path, "rt") as f:
        header_count = 0
        for line in f:
            if not line.startswith("##"):
                break
            header_count += 1

    df = pd.read_table(path, skiprows=header_count, sep="\t")
    df.columns = df.columns.str.lstrip("#")
    info_df = pd.DataFrame(df["INFO"].apply(parse_field_list).to_list())
    df = pd.concat([df[["CHROM", "POS", "REF", "ALT"]], info_df[["TYPE", "DP", "AO", "RO"]]], axis=1)

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