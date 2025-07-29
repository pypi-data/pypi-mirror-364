# AIVA Sample CSV Processor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenCRAVAT](https://img.shields.io/badge/OpenCRAVAT-2.2.0+-green.svg)](https://github.com/KarchinLab/open-cravat)

A Python package for processing OpenCRAVAT CSV output files and generating sample CSVs for database import. This tool helps streamline the workflow from variant calling to database import by converting OpenCRAVAT annotations into structured CSV files ready for database loading.

## Features

- Process OpenCRAVAT CSV files into structured database-ready formats
- Generate VRS IDs for variants using the aiva-vrs library
- Create separate CSV files for variants, transcript consequences, and sample variants
- Support for multi-sample VCF inputs
- Handle various zygosity, quality, and depth metrics
- Optional compression of output files
- Customizable sample metadata

## Installation

### Quick Install

```bash
pip install aiva-sample-processor
```

### Development Install

```bash
git clone https://github.com/MHSPL/aiva-sample-processor.git
cd aiva-sample-processor
pip install -e .
```

### Dependencies

This package requires:

- Python 3.8+
- open-cravat 2.2.0+
- aiva-vrs 0.1.0+
- pandas
- tqdm
- psycopg2-binary

All dependencies will be installed automatically when installing with pip.

## Usage

### 1. Run OpenCRAVAT

First, run OpenCRAVAT on your VCF file to generate the input CSV:

```bash
# Install OpenCRAVAT modules (first time only)
oc module install-base
oc module install csvreporter

# Run OpenCRAVAT
oc run input.vcf -l hg38 -t csv 
```

### 2. Process the OpenCRAVAT Output

Use the aiva-sample-processor command to process the OpenCRAVAT output:

```bash
aiva-sample-processor --input input.vcf.variant.csv --output-dir output_csvs
```

### Command Line Options

```
usage: aiva-sample-processor [-h] --input INPUT --output-dir OUTPUT_DIR [--assembly {GRCh37,GRCh38}]
                           [--no-compress] [--owner-id OWNER_ID] [--group-id GROUP_ID]
                           [--is-public {true,false}] [--sample-type SAMPLE_TYPE]
                           [--status STATUS] [--review-status REVIEW_STATUS]
                           [--view-status VIEW_STATUS] [--archive-status ARCHIVE_STATUS]
                           [--clinical-notes CLINICAL_NOTES] [--phenotype-terms PHENOTYPE_TERMS]

Generate CSVs for importing sample variants into the database.

required arguments:
  --input INPUT          Path to OpenCRAVAT CSV file
  --output-dir OUTPUT_DIR
                        Directory to write output CSVs to

optional arguments:
  --assembly {GRCh37,GRCh38}
                        Genome assembly (default: GRCh38)
  --no-compress         Do not compress output files with gzip
  --owner-id OWNER_ID   User ID of the owner (default: user-1)
  --group-id GROUP_ID   Group ID for the samples
  --is-public {true,false}
                        Whether samples are public (default: false)
  --sample-type SAMPLE_TYPE
                        Type of sample (default: blood)
  --status STATUS       Sample processing status (default: processed)
  --review-status REVIEW_STATUS
                        Review status of the sample (default: not_reviewed)
  --view-status VIEW_STATUS
                        View status of the sample (default: none)
  --archive-status ARCHIVE_STATUS
                        Archive status of the sample (default: active)
  --clinical-notes CLINICAL_NOTES
                        Clinical notes for the sample
  --phenotype-terms PHENOTYPE_TERMS
                        JSON array of phenotype terms (default: [])
```

## Output Files

The tool generates the following CSV files:

1. **variants.csv(.gz)**: Contains variant information with VRS IDs
2. **transcript_consequences.csv(.gz)**: Contains transcript consequences for each variant
3. **sample_variants.csv(.gz)**: Contains sample-specific variant information
4. **samples.csv**: Contains sample metadata

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenCRAVAT](https://github.com/KarchinLab/open-cravat) for providing the annotation framework
- [GA4GH VRS](https://vrs.ga4gh.org/) for the variant representation standard
