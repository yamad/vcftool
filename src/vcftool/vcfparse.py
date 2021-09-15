"""Parser for VCF v4.1 files

The parse format follows the spec at https://samtools.github.io/hts-specs/VCFv4.1.pdf.

Later VCF formats are not supported.
"""
import json
import logging
from typing import Optional, Sequence, TextIO

import requests

from vcftool.types import MISSING_VALUE, Consequence

logger = logging.getLogger(__name__)


class VCFParseError(Exception):
    """Generic parse error for VCF file"""


class NotAFieldListError(VCFParseError):
    """Expected comma-separated list of key=value pairs"""


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


def most_serious_consequence(
    consequence: Optional[dict], default=MISSING_VALUE
) -> Optional[str]:
    """Return the most deleterious consequence from ExAC consequence record

    The order is defined by the `vcftool.types.Consequence` enum

    ExAC API will return either a null or a JSON object under the
    `consequence` attribute, so we handle both possiblities here. If
    no value is available, return `default` value.
    """
    if consequence is None:
        return default

    def severity(conseq):
        return getattr(Consequence, conseq, Consequence.unknown)

    sorted_effects = sorted(consequence.keys(), key=severity)
    return next(iter(sorted_effects), default)


def count_header_lines(file: TextIO, header_prefix="##"):
    """Return number of header lines, indicated by `header_prefix`, in `file`"""
    header_count = 0
    for line in file:
        if not line.startswith(header_prefix):
            break
        header_count += 1
    return header_count


def fetch_exac_bulk_variant(variant_ids: Sequence[str]):
    """Fetch variant data for multiple variants from ExAC /bulk/variant endpoint"""
    res = requests.post(
        "http://exac.hms.harvard.edu/rest/bulk/variant",
        data=json.dumps(variant_ids),
        timeout=2,
    )

    res.raise_for_status()
    return res.json()


def fetch_exac_variant(variant_id):
    """Fetch variant data for a single variant from ExAC /variant endpoint"""
    res = requests.get(
        f"http://exac.hms.harvard.edu/rest/variant/{variant_id}", timeout=2
    )
    res.raise_for_status()
    return res.json()
