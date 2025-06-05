import os,sys,glob,random,re,gzip,argparse
#from itertools import combinations
from collections import Counter
#from statstics import mean 
import xml.etree.ElementTree as elemTree

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lib.keyword_search import searchHabitat

def iterPackage(iFN):
    if iFN.endswith("gz"): iFP = gzip.open(iFN,'rt',encoding='utf-8')
    else: iFP = open(iFN,'r',encoding='utf-8')
    for i in range(2): iFP.readline() ## Skip
    start = "<Package>"
    #end = "</Package>"
    lines = [iFP.readline()]
    if lines[0].strip() != start: raise ValueError()
    for line in iFP:
        if start == line.strip():
            yield lines
            lines = [line,]
        else: lines.append(line)    
    yield lines[:-1] ## </PackageSet>

def iterSample(iFN):
    if iFN.endswith("gz"): iFP = gzip.open(iFN,'rt',encoding='utf-8')
    else: iFP = open(iFN,'r',encoding='utf-8')
    for i in range(2): iFP.readline() ## Skip
    start = "<BioSample"
    lines = [iFP.readline()]
    if not lines[0].startswith(start): raise ValueError("Unexpected file format detected")
    for line in iFP:
        if line.startswith(start):
            yield lines
            lines = [line,]
        else: lines.append(line)    
    yield lines[:-1] ## </PackageSet>


def getIDListGTDB(gtdbmetaFN,genomeAccL):
    bioprojects, biosamples = {}, {} ## Sum bioproject and biosample was repeated multiple times in genomes
    #for line in open("/root/PublicResource/GTDB/GTDBmeta/targetMeta.txt"):
    iFP = open(gtdbmetaFN,'r') ## Expected ar53_metadata_r220.tsv  OR bac120_metadata_r220.tsv
    targetGenomes = {genomeAcc:0 for genomeAcc in genomeAccL}
    columns = iFP.readline().rstrip().split('\t')
    idxGenomeAcc, idxBioproject, idxBiosample = columns.index("ncbi_genbank_assembly_accession"), columns.index("ncbi_bioproject"), columns.index("ncbi_biosample")
    for line in iFP:
        values = line.rstrip('\n').split('\t')
        genomeAcc, bioprojectID, biosampleID = values[idxGenomeAcc], values[idxBioproject], values[idxBiosample]
        if genomeAcc not in targetGenomes: continue
        bioprojects.setdefault(bioprojectID,set()) 
        bioprojects[bioprojectID].add(genomeAcc)
        biosamples.setdefault(biosampleID,set())
        biosamples[biosampleID].add(genomeAcc)
    #bioprojects, biosamples = dict.fromkeys(bioprojects,False), dict.fromkeys(biosamples,False)
    return bioprojects, biosamples

def getIDListNCBI(ncbimetaFN, genomeAccL):
    targetGenomes = {genomeAcc:0 for genomeAcc in genomeAccL}
    bioprojects, biosamples = {}, {} ## Sum bioproject and biosample was repeated multiple times in genomes
    #for line in open("/root/PublicResource/GTDB/NCBImeta/assembly_summary_genbank.txt"):

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
        bioprojects.setdefault(bioprojectID,set()) 
        bioprojects[bioprojectID].add(genomeAcc)
        biosamples.setdefault(biosampleID,set())
        biosamples[biosampleID].add(genomeAcc)
    #bioprojects, biosamples = dict.fromkeys(bioprojects,False), dict.fromkeys(biosamples,False)
    return bioprojects, biosamples

def bioprojectSearchHabitat(pjt2T):
    habitatCnt = Counter()
    #pjt2T = pjtT.find("./Project")
    pjtDecT = pjt2T.find("./ProjectDescr")
    pjtDecTitle = pjtDecT.find("Title").text
    habitatCnt += Counter(searchHabitat(pjtDecTitle))
    if pjtDecT.find("Name") != None: pjtDecName = pjtDecT.find("Name").text
    else: pjtDecName = ""
    if pjtDecT.find("Description") != None:
        pjtDecDec = pjtDecT.find("Description").text   
        habitatCnt += Counter(searchHabitat(pjtDecDec))
    else: pjtDecDec = ""
    ## Add title of related publications?
    return [pjtDecTitle, pjtDecName, pjtDecDec],habitatCnt

def biosampleSearchHabitat(tree):
    habitatCnt = Counter()
    decT = tree.find("./Description")
    sampleTitle = decT.find("Title").text
    habitatCnt += Counter(searchHabitat(sampleTitle))
    if decT.find("Organism") != None:
        sampleTaxID = decT.find("Organism").get("taxonomy_id")
        sampleTaxname = decT.find("Organism").get("taxonomy_name")
    else: sampleTaxID, sampleTaxname = "", ""

    if decT.find("Comment") != None and \
        decT.find("Comment").find("Paragraph") != None and \
        decT.find("Comment").find("Paragraph").text != None:
        sampleComment = decT.find("Comment").find("Paragraph").text
        habitatCnt += Counter(searchHabitat(sampleComment))    
    else: sampleComment = ""
    attrT = tree.find("./Attributes")
    attrD = {}
    for s_attrT in attrT.iterfind("Attribute"):
        attrName = s_attrT.get("attribute_name")
        attrName = attrName.lower().replace('_',' ').replace('-',' ').replace('  ',' ') ## sample-type, sample type, sample   type, sample_type, Sample_type, SAMPLE TYPE, so many cases detected from diverse attribute names
        attrValue = s_attrT.text
        if attrValue != None:
            if attrName in attrD: attrD[attrName] += f' {attrValue}' ## when sample-type, sample type coexists in a biosample
            else: attrD[attrName] = attrValue
            habitatCnt += Counter(searchHabitat(attrValue))
    return [sampleTitle, sampleTaxID, sampleTaxname, sampleComment ], attrD, habitatCnt
  

def cleanText(text):
    text = text.replace('\t',' ').replace('\n',' ').replace('<sup>','').replace('</sup>','').replace('\r','')
    ## remove markers for "Bold", "Italtic", others
    text =  re.sub(r"\</?[ibpIBP]\>","",text)## Pattern, To, OriginalText
    return text.strip()

def parseArg():
    parser = argparse.ArgumentParser(description="Argument parser")
    parser.add_argument('--subject', choices=["Bioproject","Biosample","Both"], help='Target for searching habitat determining keywords', default="Both")
    parser.add_argument('--targetDB', choices=["GTDB","NCBI","Both"], help='DB referring the bioproject/biosample ID', default="Both")
    args, remaining_args = parser.parse_known_args()
    if args.targetDB == "Both" or args.targetDB == "GTDB":
        parser.add_argument('--gtdbmeta', type=str, help='Path of GTDB metadata', required=True)
    if args.targetDB == "Both" or args.targetDB == "NCBI":
        parser.add_argument('--ncbimeta', type=str, help='Path of NCBI assembly metadata',required=True)
    parser.add_argument('--genomeAccs', type=str, help='List of query genome accessions (GCA_XXXX,GCA_XXXX) or a file written genome accessions in each line',required=True)
    parser.add_argument('--printAttr', action='store_true', help='Print attributes of biosamples for debug', default=True)
    if args.subject == "Both":
        parser.add_argument('--bioprojectXML', type=str, help='bioproject XML file (bioproject.xml)',required=True) 
        parser.add_argument('--biosampleXML', type=str, help='biosample XML file (biosample_set.xml or biosample_set.xml.gz)',required=True)
        parser.add_argument('--bioprojectOut', type=str, help='Output file for bioproject',required=True) 
        parser.add_argument('--biosampleOut', type=str, help='Output file for biosample',required=True)
    if args.subject == "Bioproject":
        parser.add_argument('--bioprojectXML', type=str, help='bioproject XML file (bioproject.xml)',required=True) 
        parser.add_argument('--bioprojectOut', type=str, help='Output file for bioproject',required=True) 
    if args.subject == "Biosample":
        parser.add_argument('--biosampleXML', type=str, help='biosample XML file (biosample_set.xml or biosample_set.xml.gz)',required=True)
        parser.add_argument('--biosampleOut', type=str, help='Output file for biosample',required=True)
    args = parser.parse_args(remaining_args, namespace=args)

    if args.targetDB == "Both" or args.targetDB == "GTDB":
        if not os.path.exists(args.gtdbmeta): raise ValueError(f"GTDB metadata file not exist {args.gtdbmeta}")
    if args.targetDB == "Both" or args.targetDB == "NCBI":
        if not os.path.exists(args.ncbimeta): raise ValueError(f"NCBI metadata file not exist {args.ncbimeta}")
    if args.subject == "Both" or args.subject == "Bioproject":
        if not os.path.exists(args.bioprojectXML): raise ValueError(f"Bioproject XML file not exist {args.bioprojectXML}")
    if args.subject == "Both" or args.subject == "Biosample":
        if not os.path.exists(args.biosampleXML): raise ValueError(f"Bioproject XML file not exist {args.biosampleXML}")

    return args



def main():
    args = parseArg()
    ## Symbiont include clinical
    ## Found the habitat from bioproject or biosample or both
    print(args.genomeAccs)

    subject = args.subject
    if subject == "Both": subject = ["Bioproject","Biosample"]
    elif subject == "Bioproject": subject = ["Bioproject"]
    elif subject == "Biosample": subject = ["Biosample"]

    ## Bioproject and biosample 
    target = args.targetDB #["gtdb","summary"] ==> ["Both","GTDB","NCBI"]
    if target == "Both": targetDBs = ["GTDB","NCBI"]
    elif target == "GTDB": targetDBs = ["GTDB"]
    elif target == "NCBI": targetDBs = ["NCBI"]
    printAttr = args.printAttr

    if os.path.exists(args.genomeAccs): genomeAccL = [line.strip() for line in open(args.genomeAccs)]
    else: genomeAccL = args.genomeAccs.split(',')
    if not all([genomeAcc.startswith("GC") for genomeAcc in genomeAccL]): raise ValueError(f"Unexpected genome accessions found {genomeAccL}")
    print("Target genome acc",len(genomeAccL))




    habitats = ["Host","Artificial","Aqua","Freshwater","Groundwater","Spring","Bog","Pond","Hydrothermal","Lagoon","Acidmine","Ice","Brackish","Marine","Soil","Sediment","Modified","Extreme","Biofilm","Metagenome","SingleCell","Warning","Ambiguous","Hypersaline"] ## See SearchHabitat.py


    ## attrName.lower().replace('_',' ').replace('-',' ') ==> just remain sample type instead of sample_type, sample-type and for ,all keys, remove _- after lower()
    pickedAttrL = [["project type",'sample type','sample material',"metagenome source",'metagenomic','metagenomic source'],
             ["geo loc name","geographic location","country","geographic location (country and/or sea)","geographic location (country and/or sea, region)","geographic location (region and locality)","region","State (cntn_id)","isolation location"],
             ["isolation source","isolation Site","isolate source","collection place", "habitat", "ifsac+ category", "wastewater_type", "isolation source food", "isolation source note","source","soil type","foodon ontology term"],
             ["environment","environment (biome)","environment (feature)","environment feature", "environment material","environment (material)","environment biome","biome","env package","env biome","env feature","env material","environmental package","material","feature","source type","env broad scale", "env local scale", "env medium", "broad scale environmental context", "local scale environmental context", "environmental medium", "local environmental context"], 
             ["host", "Host Name", "specific host", "isolation source host associated"],  ## other candidates host status, bodysite, host disease, observed biotic relationship ....
             ]
            ## "note","comment", "sample comment", "subsrc_note", "Description", "note2", "subsrc-note", "subsource_note", "derived-from", "dreived-from", "deerived-from", "sample_description","value"
            ## ref biomaterial
    if "GTDB" in targetDBs:
        bioprojectGTDB, biosampleGTDB = getIDListGTDB(args.gtdbmeta,genomeAccL) ## get bioproject, biosample ids involved in bacterial genomes
        bioprojects, biosamples = bioprojectGTDB, biosampleGTDB #  bioprojects[bioprojectID].add(genomeAcc)
        print("#Bioprojects from GTDB",len(bioprojects),"#Biosamples from GTDB",len(biosamples))
    if "NCBI" in targetDBs:
        bioprojectNCBI, biosampleNCBI = getIDListNCBI(args.ncbimeta,genomeAccL) ## get bioproject, biosample ids involved in bacterial genomes
        print("#Bioprojects from NCBI",len(bioprojectNCBI),"#Biosamples from NCBI",len(biosampleNCBI))
        if "GTDB" in targetDBs:
            bioprojects, biosamples = {}, {}
            for bioprojectID in set(list(bioprojectNCBI.keys()) + list(bioprojectGTDB.keys())):
                bioprojects[bioprojectID] = bioprojectGTDB.get(bioprojectID,set()).union(bioprojectNCBI.get(bioprojectID,[]))
            for biosampleID in set(list(biosampleNCBI.keys()) + list(biosampleGTDB.keys())):
                biosamples[biosampleID] = biosampleGTDB.get(biosampleID,set()).union(biosampleNCBI.get(biosampleID,[]))
        else:
            bioprojects, biosamples = bioprojectNCBI, biosampleNCBI

    bioprojectAccs, biosampleAccs = bioprojects, biosamples
    bioprojects = {bioprojectID:False for bioprojectID in bioprojects}
    biosamples = {biosampleID:False for biosampleID in biosamples}
    print("#Related bioproject :", len(bioprojects))
    print("#Related biosample :", len(biosamples))
    # Since keyword can be found from either biosample or bioprojects,
    # here only records keyword including biosample IDs and bioproject IDs
    # after this, the biosample, bioproject, genome IDs were compared and the xml is divided
    ### it is possible to check the related bioproject after check biosample but it is required huge time to find out related bioproject data
    ### biosample is more important since a biproject include both soil samples and lake samples for comparison.
    if "Bioproject" in subject:
        xmlFN, outputFN = args.bioprojectXML, args.bioprojectOut
        if not os.path.exists(outputFN): 
            wFP = open(outputFN,'w',encoding='utf-8')
            wFP.write("ID\tTitle\tName\tDec\tType\t" + '\t'.join(habitats) + '\n')
        else: wFP = open(outputFN,'a',encoding='utf-8')
        for lines in iterPackage(xmlFN):
            tree = elemTree.fromstring("".join(lines))
            ## Grep information from tree
            # add suffix T, it represent elemental tree object
            pjtT = tree.find("./Project")
            for pjt2T in pjtT.iterfind("./Project"):
                pjtIDT = pjt2T.find("./ProjectID")
                arcIDT = pjtIDT.find("./ArchiveID")
                arcID = arcIDT.attrib["accession"]
                if arcID not in bioprojects: continue ## is not bacteiral genome involved bioproject!
                #print(arcID)
                bioprojects[arcID] = True
                pjtDec, habitatCnt = bioprojectSearchHabitat(pjt2T)
                targetT = pjt2T.find("./ProjectType/ProjectTypeSubmission/Target")
                if targetT != None: pjtType  = targetT.get("sample_scope")
                else: pjtType= ""
                wList = [arcID,] + pjtDec + [pjtType,] + [str(habitatCnt[habitat]) for habitat in habitats]
                wList = [cleanText(value) for value in wList]
                wFP.write('\t'.join(wList) + '\n')
        print(Counter(bioprojects.values()))
        print("Not detected description from XML for",[bioproject for bioproject, isdetected in bioprojects.items() if isdetected == False])
        wFP.close()

    if "Biosample" in subject:
        ## target attribute list
        xmlFN, outputFN = args.biosampleXML, args.biosampleOut
        if not os.path.exists(outputFN):
            wFP = open(outputFN, 'w',encoding='utf-8')
            wFP.write("ID\tTitle\tTaxID\tTaxname\t" + '\t'.join([attrSet[0] for attrSet in pickedAttrL]) +\
                     '\t' +'\t'.join(habitats) + '\n')
        else: wFP = open(outputFN,'a',encoding='utf-8')            
        debugD = {}
        for lines in iterSample(xmlFN):
            tree = elemTree.fromstring("".join(lines))
            idsT = tree.find("./Ids")
            idDict = {}
            for idT in idsT.iterfind("./Id"):
                dbName = idT.get("db") ## "BioSample", "WUGSC", "SRA"
                dbID = idT.text
                idDict[dbName] = dbID
            if "BioSample" not in idDict: continue #raise ValueError("No biosample id for",lines)
            biosampleID = idDict["BioSample"]
            if biosampleID not in biosamples: continue
            biosamples[biosampleID] = True   
            # return [sampleTitle, sampleTaxID, sampleTaxname], attrD, habitatCnt
            sampleInfo, attrD, habitatCnt = biosampleSearchHabitat(tree)
            sampleTitle, sampleTaxID, sampleTaxname, sampleComment = sampleInfo
            for key, value in sorted(attrD.items()):
                debugD.setdefault(key,set())
                if len(debugD[key]) < 20:
                    debugD[key].add(value)
            wList = [biosampleID,sampleTitle,sampleTaxID,sampleTaxname,]
            for attrSet in pickedAttrL:
                attrText = "|".join([attrD[attr] for attr in attrSet if attr in attrD])
                wList.append(attrText)
            wList += [str(habitatCnt[habitat]) for habitat in habitats]
            wList = [cleanText(value) for value in wList]
            wFP.write("\t".join(wList) + '\n')
        if printAttr:
            for key, values in debugD.items():
                print(key,list(sorted(values)))
        print(Counter(biosamples.values()))
        print([biosampleID for biosampleID, isdetected in biosamples.items() if isdetected == False])
   


if __name__ == "__main__": main()
