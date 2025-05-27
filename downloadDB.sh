#!/bin/bash

mkdir -p ./DB

wget -c -P ./DB https://data.ace.uq.edu.au/public/gtdb/data/releases/release220/220.0/ar53_metadata_r220.tsv.gz
wget -c -P ./DB https://data.ace.uq.edu.au/public/gtdb/data/releases/release220/220.0/bac120_metadata_r220.tsv.gz
gzip -d ./DB/ar53_metadata_r220.tsv.gz
gzip -d ./DB/bac120_metadata_r220.tsv.gz
wget -c -P ./DB https://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt
wget -c -P ./DB https://ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml
wget -c -P ./DB https://ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz
