from enum import IntEnum
from typing import NamedTuple

MISSING_VALUE = ""


class VariantRecord(NamedTuple):
    variant_id: str
    type: str
    consequence: str
    depth: str
    read_count: int
    read_percent: float
    exac_frequency: str  # pass-through string from ExAC API
    quality: str  # pass-through string from VCF


class Consequence(IntEnum):
    """Variant consequences by order of severity (worst is lowest)

    Taken from https://uswest.ensembl.org/info/genome/variation/prediction/predicted_data.html
    """

    transcript_ablation = 0
    splice_acceptor_variant = 1
    splice_donor_variant = 2
    stop_gained = 3
    frameshift_variant = 4
    stop_lost = 5
    start_lost = 6
    transcript_amplification = 7
    inframe_insertion = 8
    inframe_deletion = 9
    missense_variant = 10
    protein_altering_variant = 11
    splice_region_variant = 12
    incomplete_terminal_codon_variant = 13
    start_retained_variant = 14
    stop_retained_variant = 15
    synonymous_variant = 16
    coding_sequence_variant = 17
    mature_miRNA_variant = 18
    five_prime_UTR_variant = 19
    three_prime_UTR_variant = 20
    non_coding_transcript_exon_variant = 21
    intron_variant = 22
    NMD_transcript_variant = 23
    non_coding_transcript_variant = 24
    upstream_gene_variant = 25
    downstream_gene_variant = 26
    TFBS_ablation = 27
    TFBS_amplification = 28
    TF_binding_site_variant = 29
    regulatory_region_ablation = 30
    regulatory_region_amplification = 31
    feature_elongation = 32
    regulatory_region_variant = 33
    feature_truncation = 34
    intergenic_variant = 35
    unknown = 1000
