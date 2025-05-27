def searchHabitat(text):
    for specialChar in "-_.,()[];:/\#\"\'": 
        text = text.replace(specialChar,' ')
    ## Need to change two-word-keyword as one
    text = text.lower().replace('fresh water','freshwater').replace('homo sapience','homosapience').replace("ground water","groundwater").replace("single cell","singlecell").replace(" associated","-associated").replace("hot spring","hotspring").replace("hydrothermal vent","hydrothermalvent").replace("acid mine","acidmine")
    text = text.split() ## word
    habitats = []
    ## Most of habitats is hint for distinguish non-freshwater data

    ## Excluding
    if isHost(text): habitats.append("Host") ## human associated ## livingstocks and animal, plant, insect, algae associated
    if isArtificial(text): habitats.append("Artificial") ## foodborne, sewage

    ## Habitat determining
    if isFreshwater(text): habitats.append("Freshwater")
    if isGroundwater(text): habitats.append("Groundwater")
    if isSpring(text): habitats.append("Spring")    
    if isSoil(text): habitats.append("Soil")
    if isSediment(text): habitats.append("Sediment")
    if isBog(text): habitats.append("Bog")
    if isIce(text): habitats.append("Ice") ## Cryoconite, ice, snow, glacier
    if isPond(text): habitats.append("Pond")
    if isMarine(text): habitats.append("Marine") ## Open water
    if isBrackish(text): habitats.append("Brackish") ## Baltic sea, black sea, estuary
    if isModified(text): habitats.append("Modified") ## mesocosm, enrichment culture, dranage, contaminated environment
    if isExtreme(text): habitats.append("Extreme") ## saline, oligotrophic, ultra-
    if isAquatic(text): habitats.append("Aqua")
    if isBiofilm(text): habitats.append("Biofilm")
    if isHydrothermal(text): habitats.append("Hydrothermal")
    if isLagoon(text): habitats.append("Lagoon")
    if isAcidmine(text): habitats.append("Acidmine")
    if isHypersaline(text): habitats.append("Hypersaline")
   
    
    ## Method determining
    if isMetagenome(text): habitats.append("Metagenome")    
    if isSingleCell(text): habitats.append("SingleCell")

    ## Warning
    if isAmbiguous(text): habitats.append("Ambiguous")
    if isWarning(text): habitats.append("Warning")
    return habitats

## airborne

## Excluding
def isHost(text): ## clinic and clinic for livestock
    keywords = ["sponge", "pig", "dog","cow", "chicken", "human-associated","homosapience", "sheep", "horse", "canine", "goat", "rat", "mouse", "bovine", "potato", "cattle", "crop", "oat", "soybean", 'corn', 'rice', 'wheat', 'arabidopsis', "drosophila","crow","worm","fish", "cat","bird", "avian", "mammal", "sine","gallus","taurus","termite","rodent","duck","sativa","shellfish","larva","shrimp",
                 "endophyltic","endophyte", "epiphyltic","epiphyte","parasite", "endosymbiont", "animal", "insect" ,"host-associated", "animal-associated","plant-associated","host",
                "periodontal","serotype", "serovar", "fever", "inflammation", "nasopharynx","throat","sputum", "nares", "oropharynx", "rumen", "gut","oral","fetus", "blood", "tissue", "fece","fecal", "stool", "dung","infected", "GI tract", "infect", "infection", "leaf", "leave","stem", "midgut", "urine","uterus","skin","tung","lung","liver","spleen","intestine","intestinal","oropharyngeal","foregut","ovary","lesion","lymph","rectum","ileum","vagina","vulva","gland",
                "clinical","patient","clinic","hospital", "disease", "diseased", "pathogen", "pathogenic", "virulence", "virulent","medical"]
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isArtificial(text): 
    keywords = ["foodborne", "food", "drink", "meat", "seafood", "cheese", "milk","wine"]
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isAmbiguous(text): 
    keywords = ["mangrove"]
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]


## Habitat determining
## functionalize instead of "for statement" to add specialized rule for specific habitat
def isFreshwater(text): ## any metadata text
    keywords = ["freshwater",'lake','river','reservoir','lenthic','lentic','lotic'] ## problem in genetic reservoir, ice-forming temperature, 
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isGroundwater(text):
    keywords = ['groundwater','ground-water'] 
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isHydrothermal(text):
    keywords = ['hydrothermalvent'] 
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isHypersaline(text):
    keywords = ['hypersaline']
    keywords += [keyword+'s' for keyword in keywords] 
    detected = [keyword for keyword in keywords if keyword in text]
    if "hyper" in keywords and "saline" in keywords: detected.append(keyword)
    return detected

def isLagoon(text):
    keywords = ['lagoon'] 
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isAcidmine(text):
    keywords = ['acidmine'] 
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isSpring(text):
    keywords = ["hotspring","spring"] ## Spring excluded since it is used as both season and particualr location ## But hydrothermal spring, bog spring, sulfur spring, hot water spring, spring water  is detected...
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isSoil(text): ## including many terrestrial systems
    keywords = ["soil",  "rock", "endolithic", "endolith", "stone", "mud", "sand", "wetland","root","mycorrhiza","rhizosphere","rhizobia","nodule","desert"]  ## mud also used as sediment and soil
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isSediment(text): ## Coupled with Freshwater to detect "Freswhater sediment" e.g. bottom of lake
    keywords = ["sediment","sedimentary","seafloor","seabed"]
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isBog(text):
    keywords = ["bog", "swamp"]
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isPond(text):
    keywords = ["pond"]
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isModified(text):  ## Remove human, industrial from project description search?
    keywords = ["contamination", "contaminated", "sewage","wastewater", "waste","reactor", "bioreactor","artificial",'sludge','industrial',"farm","agriculture","agricultural", "mesocosm", "microcosm", "enrichment","mine"]
    keywords += [keyword+'s' for keyword in keywords] 
    detected = [keyword for keyword in keywords if keyword in text]
    if [word for word in text if "-contaminated" in word] and "contamination" not in detected and "contaminated" not in detected:
        detected.append("contamination")
    return detected

def isIce(text):
    keywords = ["cryoconite",'ice', 'snow', 'glacier', "glacial", "subglacial", "permafrost"]
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isExtreme(text):
    keywords = ["saline","hypersaline","oligotrophic","polar","antarctic","arctic","extreme","ultra","cold","hot","psychrophilic","barophilic","psychrophile","barophile","thermophile","thermophilic","geothermal"] 
                ## acidophile
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]
    
def isMarine(text):
    keywords = ["marine",'seawater','sea', "ocean", "seafloor","seabed","submarine"]  ## pactific, indian, atlantic, midterran
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isBrackish(text):
    keywords = ["estuary","estuarine","brackish","coastal",'baltic'] ## Bay, shipyard, baltic, balt
    keywords += [keyword+'s' for keyword in keywords] 
    detected = [keyword for keyword in keywords if keyword in text]
    #if "black" in text and "sea" in text: detected.append("blacksea")
    return detected

def isBiofilm(text): ## Biomat?
    keywords = ['biofilm'] 
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isAquatic(text):
    keywords = ['aquatic',"aqua","water",'epilimnion', 'metalimnion', 'hypolimnion','ocean',"aquifer"] 
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

## Methodology
def isMetagenome(text): 
    keywords = ["metagenomic","metagenome","mag"]
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

def isSingleCell(text): 
    keywords = ["singlecell","single-cell","sag"]
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]

## Exceptional word for warning
def isWarning(text):
    keywords = ["near","nearby","around", "beside","junction"]
    keywords += [keyword+'s' for keyword in keywords] 
    return [keyword for keyword in keywords if keyword in text]
    
