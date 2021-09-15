import argparse
import csv
import logging
import sys

from vcftool.stream import annotate_vcf_variants
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
    args = parser.parse_args(sys.argv[1:])

    annotated_variants = annotate_vcf_variants(args.vcf_file)

    writer = csv.writer(args.out_file, delimiter=",")
    writer.writerow(VariantRecord._fields)
    for record in annotated_variants:
        writer.writerow(record)


if __name__ == "__main__":
    main()
