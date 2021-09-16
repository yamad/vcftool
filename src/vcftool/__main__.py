import argparse
import csv
import logging
import sys
from typing import TextIO

from vcftool.types import VariantRecord


def main():
    """CLI for variant annotation results output to CSV"""
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Variant annotation tool")
    parser.add_argument(
        "vcf_file",
        nargs="?",
        type=argparse.FileType("rt"),
        default=sys.stdin,
        help="VCF v4.1 input file (default: stdin)",
    )
    parser.add_argument(
        "out_file",
        nargs="?",
        type=argparse.FileType("wt"),
        default=sys.stdout,
        help="Annotation output file (default: stdout)",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--batch",
        action="store_true",
        default=True,
        help="run in batch mode over entire file (default)",
    )
    group.add_argument(
        "--stream",
        action="store_true",
        default=False,
        help="run in streaming mode over entries",
    )
    args = parser.parse_args(sys.argv[1:])

    annotate(args.vcf_file, args.out_file, args.stream)


def annotate(vcf_file: TextIO, out_file: TextIO, stream=True):
    if stream:
        from vcftool.stream import annotate_vcf_variants
    else:
        from vcftool.batch import annotate_vcf_variants

    annotated_variants = annotate_vcf_variants(vcf_file)

    writer = csv.writer(out_file, delimiter=",")
    writer.writerow(VariantRecord._fields)
    for record in annotated_variants:
        writer.writerow(record)


if __name__ == "__main__":
    main()
