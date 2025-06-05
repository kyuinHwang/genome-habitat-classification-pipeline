# Genome Habitat Classification Pipeline

This repository contains a pipeline to classify the habitats of source organisms based on descriptions in Bioproject and Biosample records. It first identifies related Bioproject and Biosample accession IDs from GTDB metadata, NCBI metadata, or both, and then retrieves corresponding descriptive metadata from these records to provide habitat classification for bacterial and archaeal genomes.

---

## Features

- Accepts target taxa or genome accession list as input.
- Supports multiple metadata sources: GTDB, NCBI, or both.
- Classifies habitat using Bioproject and Biosample metadata.
- Modular scripts for easy customization and extension.

---

## Installation

This pipeline requires Python 3.10 or higher
No additional Python packages are strictly required, as the pipeline mainly uses standard libraries and subprocess calls.

Clone the repository:

```bash
git clone https://github.com/kyuinHwang/genome-habitat-classification-pipeline.git
cd genome-habitat-classification-pipeline
```

Cloning the repository takes only a few seconds on a standard desktop environment.

Before running the pipeline, you need to download the required metadata files.  
We provide a helper script `downloadDB.sh` to download most database files automatically.

To download the databases, run:

```bash
bash downloadDB.sh
```

> **Note on GTDB Metadata Files:**  
> GTDB metadata filenames (e.g., `ar53_metadata_r220.tsv.gz`, `bac120_metadata_r220.tsv.gz`) may change with each release.  
> Please check the [GTDB data releases page](https://data.ace.uq.edu.au/public/gtdb/data/releases/) for the latest filenames and update both the `downloadDB.sh` script and your `config.txt` accordingly before downloading and running the pipeline.


## System Requirements & Notes

**Tested on:** Ubuntu 24.04 (Docker container on macOS) with Python 3.12.7 and standard library only.

**Hardware:** No special hardware is required for typical use cases (e.g., analyzing genomes from a single genus or species). However, when scaling up to large datasets (e.g., all bacterial genomes), increased memory capacity may be necessary.

**Database download:** Running downloadDB.sh will download GTDB/NCBI metadata (~8.5 GB). This may take several minutes to tens of minutes depending on your internet speed.

### Configuration

By default, the pipeline uses ./config.txt for configuration parameters.
You can specify a different config file with the --config option.
The config.txt file contains paths to the metadata files, so please update it to match the locations where you downloaded the database files (Default: ./DB for downloadDB.sh)


## Usage

Two main pipeline entry points:

1. Run full pipeline from GTDB taxa

```bash
python run_gtdbtaxa2habitat_pipeline.py --target_taxa g__Nitrotoga --output_dir ./output
```
2. Run habitat classification from genome accession list
```bash
python run_accession2habitat.py --input_accessions ./examples/g__Nitortoga/genomeAccs.txt --output_dir ./output
```
Run -h on either script for detailed options.

## Scripts and Libraries

This pipeline consists of several modular scripts and library files to facilitate genome habitat classification.

The run_gtdbtaxa2habitat_pipieline.py composited by all four scripts (0_,1_,2_,3_).

The run_accession2habitat.py composited by two scripts (1_, 2_).

### Scripts (`./scripts/`)

- `0_GetGenomeListByGTDBTaxa.py`  
  Retrieves genome accession lists based on user-specified GTDB taxa.

- `1_SearchMetadataAndKeywords.py`  
  This script retrieves metadata entries for each genome using its associated BioProject or BioSample identifiers. It then scans these metadata texts for habitat-determining keywords (e.g., "freshwater", "lake", "river", "reservoir") associated with predefined habitat flags (e.g., "Freshwater"). If any of these keyword are found, the corresponding habitat flag is activated for the genome. Multiple flags may be activated per genome. For example, both "Freshwater" and "Modified" may be triggerred for a sample described as 'contaminated river'). Habitat-determining keywords and their associated flags are defined in lib/keyword_search.py.

- `2_HabitatDecisionFromMetadata.py`  
  This script determines the most likely environmental origin of each genome based on the combination of activated habitat flags. If conflicting habitat flags (e.g., "Marine" and "Freshwater") are both activated, the genome is considered to originate from an "Others". If no habitat-determining keywords were matched and no flag is activated, the genome is considered to originate from an "Unspecified". The flag-based decision logic is implemented in lib/habitat_rules.py.

- `3_JoinGTDBMeta.py`  
  Merges GTDB metadata (genome size, completeness, taxa, ...) with habitat decision for comprehensive analysis.

---

These modules are designed to be easily extendable for customization or integration with other bioinformatics pipelines.

## Output

**habitatInfo.txt (See ./examples/g__Nitrotoga/habitatInfo.txt)**
This file summarizes the inferred habitat information for each genome, based on keyword matching and classification from both BioProject and BioSample metadata.

Key fields include:

- 'bioprojectFlags': Habitat-related flags detected from the BioProject metadata, based on matched keywords.
- 'bioprojectHabitat': Habitat classification inferred from the 'bioprojectFlags'
- 'biosampleFlags': Habitat-related flags detected from the BioSample metadata.
- 'biosampleHabitat': Habitat classification inferred from the 'biosampleFlags'.
- 'sumHabitat': Final consensus classification derived from both 'bioprojectHabitat' and 'biosampleHabitat'

**Result.txt (See ./examples/g__Nitrotoga/Result.txt)**  
This file extends `habitatInfo.txt` by adding genome-level metadata (e.g., taxonomy, assembly statistics). It summarizes both the inferred habitat and basic genome information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

If you encounter a problem or have a question, please open an issue on this repository:
👉 [Submit an issue](https://github.com/kyuinHwang/genome-habitat-classification-pipeline/issues)

For direct inquiries, you may contact the maintainer at: rbdls77@gmail.com


## Reference

This pipeline was developed as part of a research project on single-cell genomics analysis of Mercer Subglacial Lake in Antarctica.

The preprint is available on Research Square:
https://www.researchsquare.com/article/rs-4392950/v1

(This link will be updated upon journal publication.)

The habitat-determining keywords, flags, habitat-determining rules available in the Supplementary Tables

Parts of this README were written or revised with the help of AI to enhance clarity and precision.
