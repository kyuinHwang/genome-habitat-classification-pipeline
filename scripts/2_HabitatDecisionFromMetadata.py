import os,sys,glob,random,re,gzip,argparse
#from itertools import combinations
from collections import Counter
#from statstics import mean 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lib.habitat_rules import habitatDecision

def parseTable(iFN,keyColumn=0):
    if type(iFN) == str: iFP = open(iFN,'r')
    else: iFP = iFN
    line = iFP.readline()
    if line.startswith("#"): line = iFP.readline()
    columns = line.rstrip('\r\n').split('\t')
    dataD = {}
    for line in iFP:
        values = line.split('\t')
        values = [value.strip() for value in values]
        accID = values[keyColumn] 
        if accID in dataD: print(f"{accID} is duplicated")
        dataD[accID] = dict(zip(columns,values))
    return columns, dataD

# habitats = ["Freshwater","Bog","Sediment","Soil","Parasite","Contam","Cryoconite","Aqua", "Marine","Brackish","Metagenome"] ## See SearchHabitat.py
#ID	Title	Name	Dec	Type	Freshwater	Bog	Sediment	Soil	Clinic	Symbiont	Artificial	Cryoconite	Aqua	Marine	Brackish	Metagenome	SingleCell

def parseArg():
    ## GTDBAccs, GTDBMetaData, NCBIMetaData, BiosampleTab, BioprojectTab
    ## python 2_HabitatDecision.py --genomeAccs=./GenomeAccsTaxa/f__Burkholderiaceae.tsv --subject=Both --targetDB=Both --gtdbmeta=/path/to/DB/bac120_metadata_r220.tsv --ncbimeta=/path/to/DB/assembly_summary_genbank.txt --bioprojectTable=./Bioprojects/f__Burkholderiaceae.tsv --biosampleTable=./Biosamples/f__Burkholderiaceae.tsv --output=./Habitat/f__Burkholderiaceae.tsv
    parser = argparse.ArgumentParser(description="Argument parser")
    parser.add_argument('--subject', choices=["Bioproject","Biosample","Both"], help='Target for searching habitat determining keywords', default="Both")
    parser.add_argument('--targetDB', choices=["GTDB","NCBI","Both"], help='DB referring the bioproject/biosample ID', default="Both")
    args, remaining_args = parser.parse_known_args()
    if args.targetDB == "Both" or args.targetDB == "GTDB":
        parser.add_argument('--gtdbmeta', type=str, help='Path of GTDB metadata', required=True)
    if args.targetDB == "Both" or args.targetDB == "NCBI":
        parser.add_argument('--ncbimeta', type=str, help='Path of NCBI assembly metadata',required=True)
    parser.add_argument('--genomeAccs', type=str, help='List of query genome accessions (GCA_XXXX,GCA_XXXX) or a file written genome accessions in each line',required=True)
    if args.subject == "Both":
        parser.add_argument('--bioprojectTable', type=str, help='Bioproject keyword search results',required=True) 
        parser.add_argument('--biosampleTable', type=str, help='Biosample keyword search results',required=True)
    if args.subject == "Bioproject":
        parser.add_argument('--bioprojectTable', type=str, help='Bioproject keyword search results',required=True) 
    if args.subject == "Biosample":
        parser.add_argument('--biosampleTable', type=str, help='Biosample keyword search results',required=True)
    parser.add_argument('--outputTable', type=str, help='Output filename', required=True)
    args = parser.parse_args(remaining_args, namespace=args)


    if args.targetDB == "Both" or args.targetDB == "GTDB":
        if not os.path.exists(args.gtdbmeta): raise ValueError(f"GTDB metadata file not exist {args.gtdbmeta}")
    if args.targetDB == "Both" or args.targetDB == "NCBI":
        if not os.path.exists(args.ncbimeta): raise ValueError(f"NCBI metadata file not exist {args.ncbimeta}")
    if args.subject == "Both" or args.subject == "Bioproject":
        if not os.path.exists(args.bioprojectTable): raise ValueError(f"Bioproject Table file not exist {args.bioprojectTable}")
    if args.subject == "Both" or args.subject == "Biosample":
        if not os.path.exists(args.biosampleTable): raise ValueError(f"Biosample Table file not exist {args.biosampleTable}")

    return args


def findRelatedGTDB(gtdbmetaFN,genomeAccL):
    bioprojects, biosamples = {}, {} ## Sum bioproject and biosample was repeated multiple times in genomes
    #for line in open("/root/PublicResource/GTDB/GTDBmeta/targetMeta.txt"):
    iFP = open(gtdbmetaFN,'r') ## Expected ar53_metadata_r220.tsv  OR bac120_metadata_r220.tsv
    targetGenomes = {genomeAcc:0 for genomeAcc in genomeAccL}
    columns = iFP.readline().rstrip('\r\n').split('\t')
    idxGenomeAcc, idxBioproject, idxBiosample = columns.index("ncbi_genbank_assembly_accession"), columns.index("ncbi_bioproject"), columns.index("ncbi_biosample")
    for line in iFP:
        values = line.rstrip('\n').split('\t')
        genomeAcc, bioprojectID, biosampleID = values[idxGenomeAcc], values[idxBioproject], values[idxBiosample]
        if genomeAcc not in targetGenomes: continue
        bioprojects[genomeAcc] = bioprojectID
        biosamples[genomeAcc] = biosampleID
    #bioprojects, biosamples = dict.fromkeys(bioprojects,False), dict.fromkeys(biosamples,False)
    return bioprojects, biosamples

def findRelatedNCBI(ncbimetaFN, genomeAccL):
    targetGenomes = {genomeAcc:0 for genomeAcc in genomeAccL}
    bioprojects, biosamples = {}, {} ## Sum bioproject and biosample was repeated multiple times in genomes

    iFP = open(ncbimetaFN,'r') ## assembly_summary_genbank.txt
    for line in iFP:
        if not line.startswith("#"): break
        columnLine = line
    columns = columnLine.lstrip('#').rstrip().split('\t')
    idxGenomeAcc, idxBioproject, idxBiosample = columns.index("assembly_accession"), columns.index("bioproject"), columns.index("biosample")

    iFP.seek(0,0)
    for line in iFP:
        if line.startswith("#"): continue
        values = line.strip().split('\t')
        genomeAcc, bioprojectID, biosampleID = values[idxGenomeAcc], values[idxBioproject], values[idxBiosample]
        if genomeAcc not in targetGenomes: continue
        bioprojects[genomeAcc] = bioprojectID
        biosamples[genomeAcc] = biosampleID
    #bioprojects, biosamples = dict.fromkeys(bioprojects,False), dict.fromkeys(biosamples,False)
    return bioprojects, biosamples

def parseBioprojectTable(bioprojectTableFN):
    #ID	Title	Name	Dec	Type	Host	Artificial	Aqua	Freshwater	Groundwater	Spring	Bog	Pond	Hydrothermal	Lagoon	Acidmine	Ice	Brackish	Marine	Soil	Sediment	Modified	Extreme	Biofilm	Metagenome	SingleCell	Warning	Ambiguous	Hypersaline
    #PRJNA262935	Soil microbial communities from Rifle, Colorado, USA - sediment 16ft 4 Metagenome	sediment metagenome	Rifle CO subsurface soil sediment (16ft).	eEnvironment	0	0	0	0	0	0	0	0	0	0	0	0	0	0	2	2	0	0	01	0	0	0	0
    iFP = open(bioprojectTableFN,'r')
    columns = iFP.readline().rstrip('\r\n').split('\t')
    habitats = columns[5:]
    bioprojectInfoD = {}
    for line in iFP:
        projectID, projectTitle, projectName, projectDec, projectType, *values = line.strip().split('\t')
        habitatCnt = Counter({habitat:int(value) for habitat, value in zip(habitats,values)})
        bioprojectInfoD[projectID] = (projectID, projectTitle, projectName, projectDec, projectType, habitatCnt)
    return bioprojectInfoD

def parseBiosampleTable(biosampleTableFN):
    #ID	Title	TaxID	Taxname	project type	geo loc name	isolation source	environment	host	Host	Artificial	Aqua	Freshwater	Groundwater	Spring	Bog	Pond	Hydrothermal	Lagoon	Acidmine	Ice	Brackish	Marine	Soil	Sediment	Modified	Extreme	Biofilm	Metagenome	SingleCell	Warning	Ambiguous	Hypersaline
    #SAMN03462093	Metagenome or environmental sample from Chloroflexi bacterium CSP1-4	1640513	Chloroflexi bacterium CSP1-4	sediment metagenome|TRUE	USA: Rifle, Colorado	sediment at 5m depth			0	0	0	0	0	0	0	0	0	0	0	0	0	00	3	0	0	0	2	0	0	0	0
    iFP = open(biosampleTableFN,'r')
    columns = iFP.readline().rstrip('\r\n').split('\t')
    habitats = columns[9:]
    biosampleInfoD = {}
    for line in iFP:
        sampleID, sampleTitle, sampleTaxID, sampleTaxname, sampleType, sampleLocation, sampleSource, sampleEnv, sampleHost, *values = line.strip().split('\t')
        habitatCnt = Counter({habitat:int(value) for habitat, value in zip(habitats,values)})
        biosampleInfoD[sampleID] = (sampleID, sampleTitle, sampleTaxID, sampleTaxname, sampleType, sampleLocation, sampleSource, sampleEnv, habitatCnt)
    return biosampleInfoD


def main():
    args = parseArg()
    ## Symbiont include clinical
    ## Found the habitat from bioproject or biosample or both
    #print(args.genomeAccs)

    subject = args.subject
    if subject == "Both": subject = ["Bioproject","Biosample"]
    elif subject == "Bioproject": subject = ["Bioproject"]
    elif subject == "Biosample": subject = ["Biosample"]

    ## Bioproject and biosample 
    target = args.targetDB #["gtdb","summary"] ==> ["Both","GTDB","NCBI"]
    if target == "Both": targetDBs = ["GTDB","NCBI"]
    elif target == "GTDB": targetDBs = ["GTDB"]
    elif target == "NCBI": targetDBs = ["NCBI"]

    if os.path.exists(args.genomeAccs): genomeAccL = [line.strip() for line in open(args.genomeAccs)]
    else: genomeAccL = args.genomeAccs.split(',')
    if not all([genomeAcc.startswith("GC") for genomeAcc in genomeAccL]): raise ValueError(f"Unexpected genome accessions found {genomeAccL}")
    print(args.genomeAccs)
    ## Get information of bioproject and biosamples
    if "Bioproject" in subject:
        bioprojectInfoD = parseBioprojectTable(args.bioprojectTable)
    if "Biosample" in subject: 
        biosampleInfoD = parseBiosampleTable(args.biosampleTable)

    ## Get bioproject IDs and biosample IDs related to genomes
    cntSameProject, cntDifProject, cntNodataProject, cntSameSample, cntDifSample, cntNodataSample = 0,0,0,0,0,0
    if "GTDB" in targetDBs and "NCBI" in targetDBs:
        bioprojectD, biosampleD = {}, {}
        bioprojectGTDB_D, biosampleGTDB_D = findRelatedGTDB(args.gtdbmeta,genomeAccL)
        bioprojectNCBI_D, biosampleNCBI_D = findRelatedNCBI(args.ncbimeta,genomeAccL)
        for genomeAcc in genomeAccL:
            bioprojectNCBI = bioprojectNCBI_D.get(genomeAcc,'')
            bioprojectGTDB = bioprojectGTDB_D.get(genomeAcc,'')
            ## Prefer bioproject written in NCBI than GTDB. ## The large scale metagenome reassembly project is assigned for more genomes in GTDB metadata 
            if bioprojectNCBI in bioprojectInfoD: 
                bioprojectD[genomeAcc] = bioprojectNCBI
                if bioprojectNCBI == bioprojectGTDB: cntSameProject += 1
                else: cntDifProject += 1
            elif bioprojectGTDB in bioprojectInfoD: 
                bioprojectD[genomeAcc] = bioprojectGTDB
                cntDifProject += 1
            else:
                bioprojectD[genomeAcc] = bioprojectNCBI
                cntNodataProject += 1
            biosampleNCBI = biosampleNCBI_D.get(genomeAcc,'')
            biosampleGTDB = biosampleGTDB_D.get(genomeAcc,'')
            ## Prefer bioproject written in NCBI than GTDB. ## The large scale metagenome reassembly project is assigned for more genomes in GTDB metadata 
            if biosampleNCBI in biosampleInfoD: 
                biosampleD[genomeAcc] = biosampleNCBI
                if biosampleNCBI == biosampleGTDB: cntSameSample += 1
                else: cntDifSample += 1
            elif biosampleGTDB in biosampleInfoD: 
                biosampleD[genomeAcc] = biosampleGTDB
                cntDifSample += 1
            else:
                biosampleD[genomeAcc] = biosampleNCBI
                cntNodataSample += 1
        print("#Project (Same, Dif, Nodata)",cntSameProject, cntDifProject, cntNodataProject)
        print("#Sample (Same, Dif, Nodata)",cntSameSample, cntDifSample, cntNodataSample)
    elif "GTDB" in targetDBs:
        bioprojectD, biosampleD = findRelatedGTDB(args.gtdbmeta,genomeAccL)
    elif "NCBI" in targetDBs:
        bioprojectD, biosampleD = findRelatedNCBI(args.ncbimeta,genomeAccL) ## get bioproject, biosample ids involved in bacterial genomes
    
    ## Bioproject # projectID, projectTitle, projectDec, projectType,
    ## Biosample # sampleID, sampleTitle, sampleTaxID, sampleTaxname, sampleType, sampleLocation, sampleSource, sampleEnv, sampleHost, 
    wFP = open(args.outputTable,'w')
    columns = "genomeAcc bioprojectID bioprojectTitle bioprojectDec bioprojectFlags bioprojectHabitat biosampleID biosampleTitle biosampleLocation biosampleSource  biosampleEnvs biosampleFlags biosampleHabitat sumHabitat".split()
    wFP.write('\t'.join(columns) + '\n')
    
    sumHabitatCnt = Counter()
    for genomeAcc in genomeAccL:
        bioprojectAcc, biosampleAcc = bioprojectD.get(genomeAcc,""), biosampleD.get(genomeAcc,"")
        projectID, projectTitle, projectName, projectDec, projectType, projectFlagCnt = bioprojectInfoD.get(bioprojectAcc,(bioprojectAcc,"","","","",Counter())) ## (projectID, projectTitle, projectName, projectDec, projectType, habitatCnt)
        sampleID, sampleTitle, sampleTaxID, sampleTaxname, sampleType, sampleLocation, sampleSource, sampleEnv, sampleFlagCnt = biosampleInfoD.get(biosampleAcc,(biosampleAcc,"","","","","","","",Counter()))
        projectEst = habitatDecision(projectFlagCnt)
        sampleEst = habitatDecision(sampleFlagCnt)
        sumEst = habitatDecision(projectFlagCnt,sampleFlagCnt)
        sumHabitatCnt[sumEst] += 1

        projectFlagStr = ','.join([flag for flag, cnt in sorted(projectFlagCnt.items(),key=lambda x:-x[1]) if cnt > 0])
        sampleFlagStr = ','.join([flag for flag, cnt in sorted(sampleFlagCnt.items(),key=lambda x:-x[1]) if cnt > 0])
        wList = [genomeAcc, projectID, projectTitle, projectDec, projectFlagStr, projectEst, sampleID, sampleTitle, sampleLocation, sampleSource, sampleEnv, sampleFlagStr, sampleEst, sumEst]
        wFP.write('\t'.join(wList) + '\n')
    for habitatName, cnt in sorted(sumHabitatCnt.items(),key=lambda x:-x[1]):
        print(habitatName, cnt)

    #for habitat in "FW FWSed. GW Spring Bog Ice Lagoon Marine MarineSed. Brackish BrackishSed. Hyd.Vent Hypersaline Acidmine Biofilm Soil Modified Unspecified Others".split():

if __name__ == "__main__": main()
