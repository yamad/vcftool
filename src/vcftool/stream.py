from typing import Iterable, TextIO

from vcftool.types import VariantRecord
from vcftool.vcfparse import (
    MISSING_VALUE,
    fetch_exac_variant,
    most_serious_consequence,
    parse_field_list,
)


def annotate_vcf_variants(vcf: TextIO) -> Iterable[VariantRecord]:
    """Generate variant records from VCF file buffer

    Usage::

        with open(path_to_file, "rt") as f:
           for record in annotate_vcf_variants(f):
               print(record)
    """
    # skip file header
    for line in vcf:
        if not line.startswith("#"):
            break

    for line in vcf:
        yield from variant_records(line.rstrip("\n"))


def variant_records(vcf_line: str) -> Iterable[VariantRecord]:
    """Generate variant record(s) from VCFv4.1 record line

    Note that one VCF line will emit 1 or more variant record,
    depending on the number of alternate alleles in the VCF line.
    """
    chrom, pos, id_, ref, alt, qual, filter_, info = vcf_line.split("\t")[:8]
    info = parse_field_list(info)

    # handle multiple alternates per VCF record
    alleles = alt.split(",")
    types = info.get("TYPE", "").split(",")
    read_counts = info.get("AO", "").split(",")

    if not len(alleles) == len(types) == len(read_counts):
        raise ValueError("malformed record. missing information for alleles")

    for allele, type_, ao in zip(alleles, types, read_counts):
        yield _make_variant_record(
            chrom, pos, id_, ref, alt, qual, filter_, info, allele, type_, ao
        )


def _make_variant_record(
    chrom, pos, id_, ref, alt, qual, filter_, info, allele, type_, ao
) -> VariantRecord:
    """Construct VariantRecord from VCF data

    Helper to construct single entry for each alternative allele. Parameters match the VCF record names and come from `variant_records`.
    """
    variant_id = f"{chrom}-{pos}-{ref}-{allele}"

    import math

    # reads for alternate / reads for reference
    ao = int(ao)
    ro = int(info.get("RO", 0))
    if ro == 0:
        read_percent = math.nan
    else:
        read_percent = ao / ro * 100

    exac_record = fetch_exac_variant(variant_id)

    return VariantRecord(
        variant_id=variant_id,
        type=type_,
        consequence=most_serious_consequence(exac_record.get("consequence", {})),
        depth=info.get("DP", MISSING_VALUE),
        read_count=ao,
        read_percent=f"{read_percent:.2f}"
        if read_percent is not math.nan
        else MISSING_VALUE,
        exac_frequency=exac_record.get("variant", {}).get("allele_freq", MISSING_VALUE),
        quality=qual,
    )
