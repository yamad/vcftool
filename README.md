# Variant annotation tool

Reads a [VCF v4.1](https://samtools.github.io/hts-specs/VCFv4.1.pdf) file and annotates each variant with key information, including major consequence/effect.

Integrates information from the [ExAC API](http://exac.hms.harvard.edu).

## Usage

Download the code, then `pip install` the package, and run the provided `vcf-annotate` tool:

    pip install .
    vcf-annotate input.vcf > output.tsv 

### Command-line help

```
$ vcf-annotate --help
usage: vcf-annotate [-h] [vcf_file] [out_file]

Variant annotation tool

positional arguments:
  vcf_file    VCF v4.1 input file (default: stdin)
  out_file    Annotation output file (default: stdout)

optional arguments:
  -h, --help  show this help message and exit
```

## Notes

Currently known to support the VCF v4.1 output of the [freeBayes](https://github.com/freebayes/freebayes) variant detector.

It does not fully support the VCF v4.1 specification, nor does it (knowingly) support later VCF specifications.



## Missing VCF Features

* Header parsing
* Structural variants
* Per-sample interpretation

## Requirements

* Python 3.9

## Development

If you contribute to development, please use the included [pre-commit](https://pre-commit.com/) template to check and format your commits:

```
pre-commit install
```