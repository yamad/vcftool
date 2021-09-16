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

    git clone https://github.com/yamad/vcftool
    cd vcftool
    python3.9 -m venv venv
    source venv/bin/activate

    pip install .
    vcf-annotate input.vcf output.csv

## Requirements

* Python 3.9

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

## Operating modes

There are two operating modes availble: streaming and batch.

The streaming mode is implemented in vanilla python. The VCF is parsed one record at a time. The benefit is that very little is held in memory at any time, but it currently sends requests to the ExAC API once for every variant id. This will be undesirable in a production environment because the ExAC API will likely throttle the requests.

The batch mode uses the pandas library to support data manipulation. The whole VCF is loaded and parsed at once. For VCF data that easily fits in memory, this is a preferable approach.

## Testing

Tests are implemented using the pytest framework. To run them,

```
pip install '.[test]'
pytest
```

## Development

If you contribute to development, please use the included [pre-commit](https://pre-commit.com/) template to check and format your commits:

```
pre-commit install
```
