import os,sys,glob,subprocess,argparse

def load_config(path):
    config = {}
    with open(path, 'r') as f:           
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  continue
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()
    return config

def configCheck(config,args):    
    #if args.targetDB == 'both' or args.targetDB == 'GTDB': ## 0_ is included in script
    if args.domain == 'bac120':
        if not os.path.exists(config['bac120_metadata']): raise ValueError(f"GTDB metadata file {config['bac120_metadata']} is absent")
    else:
        if not os.path.exists(config['ar53_metadata']): raise ValueError(f"GTDB metadata file {config['ar53_metadata']} is absent")
    if args.targetDB == 'Both' or args.targetDB == 'NCBI':
        if not os.path.exists(config['assembly_summary']): raise ValueError(f"Assembly summary file {config['assembly_summary']} is absent")
    if args.subject == 'Both' or args.subject == 'Bioproject':
        if not os.path.exists(config['bioproject_xml']): raise ValueError(f"Bioproject XML {config['bioproject_xml']} is absent")
    if args.subject == 'Both' or args.subject == 'Biosample':
        if not os.path.exists(config['biosample_xml']): raise ValueError(f"Biosample XML {config['biosample_xml']} is absent")

def prepare1stStepCmd(args, config):
    tags = ['python', './scripts/1_SearchMetadataAndKeywords.py',  f"--subject={args.subject}", f"--targetDB={args.targetDB}", f"--genomeAccs={args.output_dir}/genomeAccs.txt"]
    if args.targetDB == 'Both' or args.targetDB == 'GTDB': tags.append(f"--gtdbmeta={config['gtdbmeta']}")
    if args.targetDB == 'Both' or args.targetDB == 'NCBI': tags.append(f"--ncbimeta={config['assembly_summary']}")
    if args.subject == 'Both' or args.subject == 'Bioproject': 
        tags.append(f"--bioprojectXML={config['bioproject_xml']}")
        tags.append(f"--bioprojectOut={args.output_dir}/bioproject.txt")
    if args.subject == 'Both' or args.subject == 'Biosample': 
        tags.append(f"--biosampleXML={config['biosample_xml']}")
        tags.append(f"--biosampleOut={args.output_dir}/biosample.txt")
    #result = subprocess.run(['python', './scripts/1_SearchMetadataAndKeywords.py',  f"--subject={args.subject}", f"--targetDB={args.targetDB}" f"--genomeAccs={args.output_dir}/genomeAccs.txt", f"--gtdbmeta={config['gtdbmeta']}", f"--ncbimeta={config['assembly_summary']}", f"--bioprojectXML={config['bioproject_xml']}", f"--biosampleXML={config['biosample_xml']}", f"--bioprojectOut={args.output_dir}/bioproject.txt", f"--biosampleOut={args.output_dir}/biosample.txt", capture_output=True, text=True)    
    return tags

def prepare2ndStepCmd(args,config):
    tags = ['python', './scripts/2_HabitatDecisionFromMetadata.py',  f"--subject={args.subject}", f"--targetDB={args.targetDB}", f"--genomeAccs={args.output_dir}/genomeAccs.txt"]
    if args.targetDB == 'Both' or args.targetDB == 'GTDB': tags.append(f"--gtdbmeta={config['gtdbmeta']}")
    if args.targetDB == 'Both' or args.targetDB == 'NCBI': tags.append(f"--ncbimeta={config['assembly_summary']}")
    if args.subject == 'Both' or args.subject == 'Bioproject': 
        tags.append(f"--bioprojectTable={args.output_dir}/bioproject.txt")
    if args.subject == 'Both' or args.subject == 'Biosample': 
        tags.append(f"--biosampleTable={args.output_dir}/biosample.txt")
    tags.append(f"--outputTable={args.output_dir}/habitatInfo.txt")
    return tags

def main():
    ## bac120_metadata, ar53_metadata, assembly_summary, bioproject_xml, biosample_xml
    parser = argparse.ArgumentParser(description="Run a genome habitat classification pipeline based on GTDB taxa name\nSupports GTDB, NCBI, or both metadata sources.")
    parser.add_argument("--target_taxa", required=True, help="Target taxon name (e.g. 'g__Nitrotoga').")
    parser.add_argument("--output_dir", default='./output', help="Directory where output files will be saved (Default: ./output).")
    parser.add_argument("--config", default='./config.txt', help="Path to configuration file (Default: ./config.txt).")
    parser.add_argument("--targetDB", choices=['Both','GTDB', 'NCBI'], default='Both', help="Metadata database to extract Bioproject/Biosample information linked to genome accessions: GTDB, NCBI, or Both. (Default: Both)")
    parser.add_argument("--subject", choices=['Bioproject', 'Biosample', 'Both'], default='Both', help="Metadata source to use: Bioproject, Biosample, or Both. (Default: Both)")
    parser.add_argument("--domain", choices=['bac120', 'ar53'], default='bac120', help="Taxonomy domain: 'bac120' for Bacteria (default), 'ar53' for Archaea.") 


    args = parser.parse_args()

    config = load_config(args.config)
    configCheck(config,args)
    if args.domain == 'bac120': config['gtdbmeta'] = config['bac120_metadata']
    else: config['gtdbmeta'] = config['ar53_metadata']

    if os.path.exists(args.output_dir): raise ValueError("Output directory already exist")
    else: os.mkdir(args.output_dir)

    ### Step 0. Get Genome IDs by GTDB taxa
    subprocess.run(['python', './scripts/0_GetGenomeListByGTDBTaxa.py', f"--gtdbmeta={config['gtdbmeta']}", f"--targetTaxa={args.target_taxa}", f"--output={args.output_dir}/genomeAccs.txt"])
    
    ### Step 1. Get bioproject/biosample infomation and search habitat related keywords
    tags = prepare1stStepCmd(args,config)
    result = subprocess.run(tags)

    ### Step 2. Determine habitat
    tags = prepare2ndStepCmd(args,config)
    result = subprocess.run(tags)

    ### Step 3. Join Genome statistics from GTDB
    result = subprocess.run(['python', './scripts/3_JoinGTDBMeta.py',  f"--gtdbmeta={config['gtdbmeta']}", f"--habitatTable={args.output_dir}/habitatInfo.txt", f"--output={args.output_dir}/Result.txt"])


if __name__ == "__main__": main()
