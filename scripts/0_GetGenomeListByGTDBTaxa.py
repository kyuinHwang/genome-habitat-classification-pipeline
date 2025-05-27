import os,sys,glob,argparse

def parseArg():
    parser = argparse.ArgumentParser(description="Argument parser")
    parser.add_argument('--gtdbmeta', type=str, help='Path of GTDB metadata', required=True)
    parser.add_argument('--targetTaxa', type=str, help='Target taxa', required=True)
    parser.add_argument('--output', type=str, help='Result table file', required=True)
    #args, remaining_args = parser.parse_known_args()
    #args = parser.parse_args(remaining_args, namespace=args)
    args = parser.parse_args()
    return args


def searchTaxaCmd():
    args = parseArg()
    metadataFN, targetTaxa, outputFN = args.gtdbmeta, args.targetTaxa, args.output

    iFP,wFP = open(metadataFN,'r'), open(outputFN,'w')
    columns = iFP.readline().split('\t')
    genomeIDX, accIDX, taxaIDX = columns.index('accession'), columns.index("ncbi_genbank_assembly_accession"), columns.index("gtdb_taxonomy")
    for line in iFP:
        values = line.strip().split('\t')
        genbankID, taxaStr = values[accIDX], values[taxaIDX]
        if targetTaxa in taxaStr:
            wFP.write(f"{genbankID}\n")
    wFP.close()

#def searchTaxa():
#    #metadataFN, targetTaxa, outputFN = args.gtdbmeta, args.targetTaxa, args.output
#    metadataFN = "/root/GTDBstat/Metadata/GTDBtsvR220/bac120_metadata_r220.tsv"
#    targetTaxaL = ["f__Miltoncostaeaceae","f__Solirubrobacteraceae","f__F1-60-MAGs149","f__S36-B12","f__UBA10799","f__Nanopelagicaceae","f__Ilumatobacteraceae","f__SG8-39","f__SG8-41","f__Burkholderiaceae","f__Gallionellaceae","f__SURF-13","f__UBA2999","f__CSP1-4","f__UBA2103","f__UBA1550"]
#    for targetTaxa in targetTaxaL:
#        outputFN = f"./GenomeAccsTaxa/{targetTaxa}.tsv"
#        iFP,wFP = open(metadataFN,'r'), open(outputFN,'w')
#        columns = iFP.readline().split('\t')
#        accIDX, taxaIDX = columns.index("ncbi_genbank_assembly_accession"), columns.index("gtdb_taxonomy")
#        for line in iFP:
#            values = line.strip().split('\t')
#            genbankID, taxaStr = values[accIDX], values[taxaIDX]
#            if targetTaxa in taxaStr:
#                wFP.write(f"{genbankID}\n")
#        wFP.close()
            
#if __name__ == "__main__": searchTaxa()
if __name__ == "__main__": searchTaxaCmd()
