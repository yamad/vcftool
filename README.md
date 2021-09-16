# Variant annotation tool

Reads a [VCF v4.1](https://samtools.github.io/hts-specs/VCFv4.1.pdf) file and annotates each variant with key information, including major consequence/effect.

Integrates information from the [ExAC API](http://exac.hms.harvard.edu).

```
$ vcf-annotate --help
usage: vcf-annotate [-h] [--batch | --stream] [vcf_file] [out_file]

Variant annotation tool

positional arguments:
  vcf_file    VCF v4.1 input file (default: stdin)
  out_file    Annotation output file (default: stdout)

optional arguments:
  -h, --help  show this help message and exit
  --batch     run in batch mode over entire file (default)
  --stream    run in streaming mode over entries
```

## Quickstart

Download the code, then `pip install` the package, and run the provided `vcf-annotate` tool:

    pip install .
    vcf-annotate input.vcf output.csv

## Output

The tool outputs a CSV file with one row per variant and the following columns,

variant_id
: as CHROM-POS-REF-ALT format

type
: variant type (mis, snp, del, ins)

consequence
: most deleterious consequence of variant. follows Sequence Ontology naming and order. if not available from ExAC, the value is empty

depth
: read depth at variant site (DP in VCF INFO)

read_count
: read count supporting the variant (AO in VCF INFO)

read_percent
: percentage of reads supporting variant versus reads supporting reference. if no reference reads, the value is "inf"

exac_frequency
: allele frequency from ExAC database. if not available from ExAC, the value is empty

quality
: QUAL score from VCF entry

## Notes

Currently known to support VCF v4.1 output of the [freeBayes](https://github.com/freebayes/freebayes) variant detector.

However, it does not fully support the VCF v4.1 specification, nor does it (knowingly) support later VCF specifications.

## Missing VCF Features

* Header parsing
* Structural variants
* Per-sample interpretation

Some of these will require a more production-quality parser than the string splitting technique prototyped here.

## Requirements

* Python 3.9

## Performance

This implementation streams the VCF file to emit one record at a time so that very little is held in memory at any time. A cost of this approach is that the ExAC API is pinged once for every variant id, instead of in batches. This is likely undesirable in a production environment because the ExAC API will likely throttle the requests. Depending on the final use case, the strategy may be altered to do more in batch.

## Development

If you contribute to development, please use the included [pre-commit](https://pre-commit.com/) template to check and format your commits:

```
pre-commit install
```
