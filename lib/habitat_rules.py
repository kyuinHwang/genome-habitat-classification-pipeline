import os,sys,glob
from collections import Counter

def habitatDecision(habitatCnt1,habitatCnt2=Counter()): ## Count from bioproject and biosample OR bioproject_NCBI and bioproject_GTDB
    # TAGS, HABITATS, RULED
    tagInc = {tag:int(habitatCnt1[tag]) + int(habitatCnt2[tag]) > 0 for tag in TAGS}
    ## must include, must exclude
    for habitat in HABITATS:
        includeTags,excludeTags = RULED[habitat]["include"], RULED[habitat]["exclude"]
        if all([tagInc[tag] for tag in includeTags]) and not any ([tagInc[tag] for tag in excludeTags]):
            break
    else: habitat = "Others"
    return habitat
    #if all([habitatSum[habitat] for habitat in ["Marine","Sediment"]]) and not any([habitatSum[habitat] for habitat in ["Lagoon","Brackish","Spring","Bog","Pond","Ice","Groundwater","Modified","Acidmine","Hydrothermal","Freshwater","Biofilm","Hypersaline"]]): decision = "Marine Sed."
    

## Initialize RULED
RULETXT = """
Habitat	Host	Artificial	Ambiguous	Freshwater	Groundwater	Spring	Bog	Ice	Lagoon	Marine	Brackish	Hydrothermal	Hypersaline	Acidmine	Biofilm	Soil	Sediment	Modified	Pond	Aqua	Extreme	Metagenome	SingleCell	Warning
FW	Exclude	Exclude	Exclude	Include	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed
FWSed.	Exclude	Exclude	Exclude	Include	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Include	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed
GW	Exclude	Exclude	Exclude	Allowed	Include	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Allowed	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
Spring	Exclude	Exclude	Exclude	Allowed	Allowed	Include	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed
Bog	Exclude	Exclude	Exclude	Allowed	Exclude	Exclude	Include	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Allowed	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed
Ice	Exclude	Exclude	Exclude	Allowed	Exclude	Exclude	Exclude	Include	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
Lagoon	Exclude	Exclude	Exclude	Allowed	Exclude	Exclude	Exclude	Exclude	Include	Allowed	Allowed	Exclude	Exclude	Exclude	Exclude	Allowed	Allowed	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
Marine	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Include	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
MarineSed.	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Include	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Include	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
Brackish	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Include	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
BrackishSed.	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Include	Exclude	Exclude	Exclude	Exclude	Allowed	Include	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
Hyd.Vent	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Allowed	Include	Exclude	Exclude	Exclude	Allowed	Allowed	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
Hypersaline	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Exclude	Allowed	Allowed	Include	Exclude	Exclude	Allowed	Allowed	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
Acidmine	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	include	Exclude	Allowed	Allowed	Allowed	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
Biofilm	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Include	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed
Soil	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Include	Allowed	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed
Modified	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Exclude	Allowed	Allowed	Allowed	Include	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed
Unspecified	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed
Others	Exclude	Exclude	Exclude	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed	Allowed
""".strip()


TAGS, *lines = RULETXT.splitlines()
TAGS = TAGS.strip().split()[1:]
RULED = {} ## "Marine":{"include":("Marine"..), "exclude":("Host","Artificial")}  #"allowed": {} ## function to include either one of two words?
HABITATS = []
for line in lines:
    habitat, *rules = line.strip().split()
    RULED[habitat] = {"allowed":[],"exclude":[],"include":[]}
    for tag, ttype in zip(TAGS,rules):
        RULED[habitat][ttype.lower()].append(tag)
    HABITATS.append(habitat)








