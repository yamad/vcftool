"""Parser for VCF v4.1 files

The parse format follows the spec at https://samtools.github.io/hts-specs/VCFv4.1.pdf.

Later VCF formats are not supported.
"""
import argparse
import csv
import logging
import sys
from collections import namedtuple
from typing import TextIO, Union, Sequence, Optional

from vcftool import exac
from vcftool.vcftypes import VCFMeta, Consequence

logger = logging.getLogger(__name__)

MISSING_VALUE = ""

class VCFParseError(Exception):
    """Generic parse error for VCF file"""


class NotAKeyValueError(VCFParseError):
    """Did not get expected key=value pair"""


class NotAFieldListError(VCFParseError):
    """Expected comma-separated list of key=value pairs"""


def parse_header(vcf: TextIO, skip: bool = False) -> VCFMeta:
    """Consume and parse VCF header lines"""
    vcfmeta = VCFMeta()

    for line in vcf:
        if not line.startswith("##"):
            break

        if skip:
            continue

        try:
            line = line.lstrip("#")
            line = line.rstrip("\n")
            key, value = parse_key_value(line)
        except VCFParseError as err:
            logger.info("Failed on line: %s", line)
            raise

        if key == "INFO":
            vcfmeta.infos[value["ID"]] = value
        elif key == "FILTER":
            vcfmeta.filters[value["ID"]] = value
        elif key == "FORMAT":
            vcfmeta.formats[value["ID"]] = value
        elif key == "ALT":
            vcfmeta.alts[value["ID"]] = value
        elif key == "contig":
            vcfmeta.contigs[value["ID"]] = value
        elif key in ["SAMPLE", "PEDIGREE"]:
            logger.warning("%s header fields are not parsed yet", key)
        else:
            vcfmeta.meta[key] = value

    return vcfmeta


def parse_key_value(line: str) -> tuple[str, Union[str, dict]]:
    try:
        key, value = line.split("=", maxsplit=1)
    except ValueError:
        raise NotAKeyValueError("malformed key=value line")

    if value.startswith("<"):
        value = value.strip("<>")  # strip brackets
        value = parse_field_list(value, field_sep=",")

    return key, value


def parse_field_list(input: str, field_sep: str = ";", kv_sep: str = "=") -> dict:
    """Convert list of key-value pairs into dictionary

    The expected input format is a string of key-value pairs,
    with the key and value separated by the `kv_sep` and each
    pair separated by the `field_sep`.

    The `field_sep` and `kv_sep` separator characters are
    always interpreted as separators, and cannot be elsewhere
    in the input string.

    Examples
    --------

    >>> parse_field_list("A=1;B=2;C=3;")
    { "A": 1, "B": 2, "C": 3 }
    >>> parse_field_list("A!1,B!2,C!3", field_sep=",", kv_sep="!")
    { "A": 1, "B": 2, "C": 3 }
    >>> parse_field_list("A=1;B='=';")
    Traceback (most recent call last):
    ...
    NotAFieldListError: ...
    """
    try:
        fields = input.split(field_sep)
        kv_pairs = (f.split(kv_sep) for f in fields)

        return {k: v for k, v in kv_pairs}
    except ValueError as err:
        raise NotAFieldListError(
            f"Expected {field_sep}-separated list of key{kv_sep}value pairs: {input}"
        ) from err


def annotate_vcf_variants(vcf: TextIO, out_buffer: TextIO):
    writer = csv.writer(out_buffer, delimiter=",")
    meta = parse_header(vcf, skip=True)

    writer.writerow(["variant_id", "type", "effect", "depth", "variant_count", "read_percent", "exac_freq", "quality"])
    for line in vcf:
        for record in variant_records(line.rstrip("\n")):
            writer.writerow(record)

VariantRecord = namedtuple("VariantRecord", "variant_id type effect depth read_count read_percent exac_frequency quality")


def variant_records(vcf_line: str):
    """Generate variant record(s) from VCFv4.1 record line

    Note that one VCF line will emit 1 or more variant record,
    depending on the number of alternate alleles in the VCF line.
    """
    chrom, pos, id_, ref, alt, qual, filter_, info = vcf_line.split("\t")[:8]
    info = parse_field_list(info)

    alleles = alt.split(",")
    types = info.get("TYPE", "").split(",")
    read_counts = info.get("AO", "").split(",")

    if not len(alleles) == len(types) == len(read_counts):
        raise ValueError("malformed record. missing information for alleles")

    depth = info.get("DP", MISSING_VALUE)

    for allele, type_, read_count in zip(alleles, types, read_counts):
        variant_id = f"{chrom}-{pos}-{ref}-{allele}"
        read_count = int(read_count)
        read_percent = (read_count + 1) / (int(info.get("RO", 0)) + 1) * 100

        exac_record = exac.fetch_variant(variant_id)
        major_effect = most_serious_consequence(exac_record.get("consequence", {}))
        allele_frequency = exac_record.get("variant", {}).get("allele_freq", MISSING_VALUE)

        yield VariantRecord(variant_id, type_, major_effect, depth, read_count, f"{read_percent:.2f}", allele_frequency, qual)


def most_serious_consequence(consequence: Optional[dict]) -> Optional[str]:
    """Return the most deleterious consequence from ExAC consequence record

    Sort by order of Consequence enum
    """
    if consequence is None:
        return MISSING_VALUE

    def severity(conseq):
        return getattr(Consequence, conseq, Consequence.unknown)

    sorted_effects = sorted(consequence.keys(), key=severity)
    return next(iter(sorted_effects), MISSING_VALUE)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Variant annotation tool")
    parser.add_argument("vcf_file", nargs="?", type=argparse.FileType("rt"), default=sys.stdin, help="VCF v4.1 input file (default: stdin)")
    parser.add_argument("out_file", nargs="?", type=argparse.FileType("wt"), default=sys.stdout, help="Annotation output file (default: stdout)")
    args = parser.parse_args(sys.argv[1:])

    annotate_vcf_variants(args.vcf_file, args.out_file)


if __name__ == "__main__":
    with open("/Users/jyh/Downloads/tempus_challenge_data.vcf", "rt") as f:
        with open("output.tsv", "wt") as out:
            annotate_vcf_variants(f, out)