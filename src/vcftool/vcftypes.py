"""VCF v4.1 Types"""
from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import NewType, TextIO

Id = NewType("Id", str)
Length = NewType("Length", int)
Description = NewType("Description", str)

class InfoType(Enum):
    Integer = "Integer"
    Float = "Float"
    Flag = "Flag"
    Character = "Character"
    String = "String"

class Info:
    id: Id
    number: str  # TODO: make acceptable values more explicit
    type: InfoType
    description: Description

class FormatType(Enum):
    Integer = "Integer"
    Float = "Float"
    Character = "Character"
    String = "String"

class Format:
    id: Id
    number: str  # TODO: make acceptable values more explicit
    type: FormatType
    description: Description


# AltId is usually one of [DEL, INS, DUP, INV, CNV, DEL:ME, INS:ME, DUP:TANDEM]
# However, it can be an unrestricted colon-separated list
AltId = NewType("AltId", str)

class Alt:
    id: AltId
    description: Description

Contig = NewType("Contig", dict)

@dataclass
class VCFMeta:
    meta: dict = field(default_factory=dict) # all unstructured/unspecified header lines
    infos: dict[Id, Info] = field(default_factory=dict)
    filters: dict[Id, Description] = field(default_factory=dict)
    formats: dict[Id, Format] = field(default_factory=dict)
    alts: dict[Id, Alt] = field(default_factory=dict)
    contigs: dict[Id, Contig] = field(default_factory=dict)


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