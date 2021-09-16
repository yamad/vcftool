import io
from pathlib import Path

import pytest

from vcftool.__main__ import annotate

sample_csv_result = [
    "variant_id,type,consequence,depth,read_count,read_percent,exac_frequency,quality",
    "1-931393-G-T,snp,,4124,95,2.3579051873914123,,2.17938e-13",
    "1-6228297-GAAAAAG-GAAAAG,del,,4340,24,0.5568445475638051,,9.54689e-14",
    "1-7797043-G-A,snp,,3468,20,0.580046403712297,,1.83222e-14",
    "1-7811328-CAAAAAAAAT-CAAAAAAAT,del,,2238,22,1.0009099181073704,,0",
    "1-9782556-C-T,snp,intron_variant,1222,562,85.15151515151516,0.3341455329023703,15959.2",
    "1-10292359-CATATATATATATA-CATATATATATA,del,,2232,70,3.298774740810556,,2.62298e-13",
    "1-10292359-CATATATATATATA-CATATATATATATATA,ins,,2232,30,1.413760603204524,,2.62298e-13",
    "1-10318744-C-A,snp,,2532,32,1.28,,0",
    "1-10363203-GA-TT,mnp,,2346,30,1.2975778546712802,,0",
    "1-10363209-G-T,snp,,2560,42,1.6679904686258933,,0",
    "1-10435441-TTTGTTGTTGTTGTTGTTGT-TTTGTTGTTGTTGTTGT,del,,2396,54,2.3156089193825045,,0",
    "1-26349532-GCCTCCTCCTCCTCCTC-GCCTCCTCCTCCTC,del,,3438,102,3.07599517490953,,3.99714e-13",
    "1-26507394-G-A,snp,splice_region_variant,2122,996,88.45470692717583,0.011213089902451885,27617.2",
    "1-45798555-T-C,snp,non_coding_transcript_exon_variant,3926,3924,196200.0,0.9255142066055771,141777",
]


@pytest.mark.parametrize("is_stream", [True, False], ids=["stream", "batch"])
def test_sample_file(is_stream):
    """Run end-to-end test in both modes"""
    sample_vcf_path = Path("tests/sample.vcf")
    out_buffer = io.StringIO()

    with open(sample_vcf_path, "rt") as infile:
        annotate(infile, out_buffer, stream=is_stream)

    out_buffer.seek(0)

    assert out_buffer.read().splitlines() == sample_csv_result
