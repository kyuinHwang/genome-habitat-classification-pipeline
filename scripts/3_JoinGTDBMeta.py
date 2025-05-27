import os,sys,glob,argparse

def parseArg():
    parser = argparse.ArgumentParser(description="Argument parser")
    parser.add_argument('--gtdbmeta', type=str, help='Path of GTDB metadata', required=True)
    parser.add_argument('--targetColumns', type=str, help='Columns of GTDB metadata which should be remained in joined table', default="accession,checkm_completeness,checkm_contamination,contig_count,n50_scaffolds,genome_size,gtdb_taxonomy,gtdb_representative")
    parser.add_argument('--habitatTable', type=str, help='Habitat file', required=True)
    parser.add_argument('--output', type=str, help='Output file', required=True)
    args, remaining_args = parser.parse_known_args()
    #args = parser.parse_args(remaining_args, namespace=args)
    return args

## accession       ambiguous_bases checkm2_completeness    checkm2_contamination   checkm2_model   checkm_completeness     checkm_contamination    checkm_marker_count     checkm_marker_lineage   checkm_marker_set_count checkm_strain_heterogeneity     coding_bases    coding_density  contig_count    gc_count        gc_percentage   genome_size     gtdb_genome_representative      gtdb_representative     gtdb_taxonomy   gtdb_type_designation_ncbi_taxa gtdb_type_designation_ncbi_taxa_sources gtdb_type_species_of_genus      l50_contigs     l50_scaffolds   longest_contig  longest_scaffold        lsu_23s_contig_len      lsu_23s_count   lsu_23s_length  lsu_23s_query_id        lsu_5s_contig_len       lsu_5s_count    lsu_5s_length   lsu_5s_query_id lsu_silva_23s_blast_align_len   lsu_silva_23s_blast_bitscore    lsu_silva_23s_blast_evalue      lsu_silva_23s_blast_perc_identity       lsu_silva_23s_blast_subject_id  lsu_silva_23s_taxonomy  mean_contig_length      mean_scaffold_length    mimag_high_quality      mimag_low_quality       mimag_medium_quality    n50_contigs     n50_scaffolds   ncbi_assembly_level     ncbi_assembly_name      ncbi_assembly_type      ncbi_bioproject ncbi_biosample  ncbi_contig_count       ncbi_contig_n50 ncbi_country    ncbi_date       ncbi_genbank_assembly_accession ncbi_genome_category    ncbi_genome_representation      ncbi_isolate    ncbi_isolation_source   ncbi_lat_lon    ncbi_molecule_count     ncbi_ncrna_count        ncbi_organism_name      ncbi_protein_count      ncbi_refseq_category    ncbi_rrna_count ncbi_scaffold_count     ncbi_scaffold_l50       ncbi_scaffold_n50       ncbi_scaffold_n75       ncbi_scaffold_n90       ncbi_seq_rel_date       ncbi_spanned_gaps       ncbi_species_taxid      ncbi_ssu_count  ncbi_strain_identifiers ncbi_submitter  ncbi_taxid      ncbi_taxonomy   ncbi_taxonomy_unfiltered        ncbi_total_gap_length   ncbi_total_length       ncbi_translation_table  ncbi_trna_count ncbi_type_material_designation  ncbi_ungapped_length    ncbi_unspanned_gaps     ncbi_wgs_master protein_count   scaffold_count  ssu_contig_len  ssu_count       ssu_gg_blast_align_len  ssu_gg_blast_bitscore   ssu_gg_blast_evalue     ssu_gg_blast_perc_identity      ssu_gg_blast_subject_id ssu_gg_taxonomy ssu_length      ssu_query_id    ssu_silva_blast_align_len       ssu_silva_blast_bitscore        ssu_silva_blast_evalue  ssu_silva_blast_perc_identity   ssu_silva_blast_subject_id      ssu_silva_taxonomy      total_gap_length        trna_aa_count   trna_count      trna_selenocysteine_count


def searchTaxaCmd():
    args = parseArg()
    metadataFN, targetColumns, habitatFN, outputFN = args.gtdbmeta, args.targetColumns, args.habitatTable, args.output
    if os.path.exists(outputFN): raise ValueError("Outputfile already exists")

    habitatFP = open(habitatFN,'r')
    habitatColumns = habitatFP.readline().rstrip().split('\t')
    habitatD = {}
    for line in habitatFP:
        values = line.strip('\r\n').split('\t')
        genbankID = values[0]
        habitatD[genbankID] = values
        if genbankID == '': print(values)

    targetColumns = targetColumns.split(',')
    metadataFP = open(metadataFN) ## GTDB metadata
    metadataColumns = metadataFP.readline().rstrip().split('\t')
    if len(set(targetColumns) - set(metadataColumns)) > 0: raise ValueError(f"Unexpected columns was included {set(targetColumns)-set(metadataColumns)}")
    genomeIDX, genbankIDX = [metadataColumns.index(column) for column in ('accession',"ncbi_genbank_assembly_accession")]
    targetIDXs = [metadataColumns.index(column) for column in targetColumns]
    metadataD = {}
    for line in metadataFP:
        values = line.strip('\r\n').split('\t')
        genbankID = values[genbankIDX]
        if genbankID in habitatD: metadataD[genbankID] = [values[idx] for idx in targetIDXs]

    outputFP = open(outputFN,'w')
    outputFP.write('\t'.join(habitatColumns + targetColumns)+'\n')
    dataNotFoundL = []
    for genbankID,habitatValues in habitatD.items():
        metadataValues = metadataD.get(genbankID,[])
        if metadataValues == []: dataNotFoundL.append(genbankID)
        outputFP.write('\t'.join(habitatValues + metadataValues) + '\n')
    if len(dataNotFoundL) > 0:
        print(f"Warning : gtdb data was absent for {habitatFN} {dataNotFoundL}")



if __name__ == "__main__": searchTaxaCmd()
