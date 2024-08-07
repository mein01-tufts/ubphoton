import sys, argparse
import numpy as np
import ROOT as rt

parser = argparse.ArgumentParser("Make energy histograms from a bnb nu overlay ntuple file")
parser.add_argument("-i", "--infile", type=str, required=True, help="input ntuple file")
parser.add_argument("-o", "--outfile", type=str, default="NpNgOutput.root", help="output root file name")
parser.add_argument("-fc", "--fullyContained", action="store_true", help="only consider fully contained events")
parser.add_argument("-ncc", "--noCosmicCuts", action="store_true", help="don't apply cosmic rejection cuts")
args = parser.parse_args()

#needed for proper scaling of error bars:
#rt.TH1.SetDefaultSumw2(rt.kTRUE)

#open input file and get event and POT trees
ntuple_file = rt.TFile(args.infile)
eventTree = ntuple_file.Get("EventTree")
potTree = ntuple_file.Get("potTree")

#scale histograms to expected event counts from POT in runs 1-3: 6.67e+20
targetPOT = 6.67e+20
targetPOTstring = "6.67e+20" #for plot axis titles

#calculate POT represented by full ntuple file after applying cross section weights
ntuplePOTsum = 0.
for i in range(potTree.GetEntries()):
    potTree.GetEntry(i)
    ntuplePOTsum = ntuplePOTsum + potTree.totGoodPOT

#define histograms to fill
#we will write histograms to output file for:
onePhotonHist = rt.TH1F("1Photon_nProtonHist", "Energy of NC events with N proton(s) and 1 photon",24,0,6)
twoPhotonHist = rt.TH1F("2Photon_nProtonHist", "Energy of NC events with N proton(s) and 2 photons",24,0,6)
threePhotonHist = rt.TH1F("3Photon_nProtonHist", "Energy of NC events with N proton(s) and 3+ photons",24,0,6)

#set histogram axis titles and increase line width
def configureHist(h):
    h.GetYaxis().SetTitle("events per "+targetPOTstring+" POT")
    h.GetXaxis().SetTitle("energy (GeV)")
    h.SetLineWidth(2)
    return h

#scale the histograms based on total good POT
onePhotonHist = configureHist(onePhotonHist)
twoPhotonHist = configureHist(twoPhotonHist)
threePhotonHist = configureHist(threePhotonHist)

#set detector min/max and fiducial width (cm)
xMin, xMax = 0, 256
yMin, yMax = -116.5, 116.5
zMin, zMax = 0, 1036
fiducialWidth = 10

trueFiducialCut = 0
trueCosmicCut = 0
trueCCcut = 0

NCcounter = 0

recoFound = 0
#begin loop over events in ntuple file
for i in range(eventTree.GetEntries()):
    eventTree.GetEntry(i)

    if eventTree.foundVertex != 1:
        continue
    
    recoFound += 1
#cut everything with a vertex within fiducialWidth (10cm) of detector wall
    if eventTree.trueVtxX <= (xMin + fiducialWidth) or eventTree.trueVtxX >= (xMax - fiducialWidth) or \
        eventTree.trueVtxY <= (yMin + fiducialWidth) or eventTree.trueVtxY >= (yMax - fiducialWidth) or \
        eventTree.trueVtxZ <= (zMin + fiducialWidth) or eventTree.trueVtxZ >= (zMax - fiducialWidth):
        trueFiducialCut += 1
        
        
#cut out cosmics: this cuts events tagged as overlapping w/cosmics
#NTS: will need algorithm for this when using reco/real data - upping fiducial to 12-13cm
#seems like the way to go re: assuring cosmics are cut
    if eventTree.vtxFracHitsOnCosmic >= 1.:
        trueCosmicCut += 1
        

#cut charge current events
    if eventTree.trueNuCCNC != 1:
        trueCCcut += 1
        

#determine whether there are photons as secondary particles
#need a list of where photons occur, can then use len() as the photon counter later
    photonInSecondary = False
    primList = []
    photonIndexList = []
    for x in range(len(eventTree.trueSimPartTID)):
        if eventTree.trueSimPartTID[x] == eventTree.trueSimPartMID[x]:
            primList.append(eventTree.trueSimPartTID[x])
#iterate through sim parts to find photons
    for x in range(len(eventTree.trueSimPartPDG)):
        if eventTree.trueSimPartPDG[x] == 22:
#check for photon's mother particle in the primary list - if it's there, then append this true photon to the list
            if eventTree.trueSimPartMID[x] in primList:
                photonIndexList.append(x)
                photonInSecondary = True
#in another case, check if the photon has coordinates within 1.5 mm of those of the event vertex - if so, add photon to the list
            elif abs(eventTree.trueSimPartX[x] - eventTree.trueVtxX) <= 0.15 and abs(eventTree.trueSimPartY[x] - eventTree.trueVtxY) <= 0.15 and abs(eventTree.trueSimPartZ[x] -eventTree.trueVtxZ) <= 0.15:
                photonIndexList.append(x)
                photonInSecondary = True

#discard event if no secondary photon is found
    if photonInSecondary == False:
        continue

#check for charged pions - we want to exclude any
    piPlusPresent = False
    for x in range(len(eventTree.truePrimPartPDG)):
        if abs(eventTree.truePrimPartPDG[x] == 211):
            piPlusPresent = True
            break
    if piPlusPresent == True:
        continue

#If proton present in primary particles, checks that its kinetic energy exceeds 60mev - count it if so
    protonPresent = False
    nProtons = 0
    for x in range(len(eventTree.truePrimPartPDG)):
        if eventTree.truePrimPartPDG[x] == 2212:
            pVector = np.square(eventTree.truePrimPartPx[x]) + np.square(eventTree.truePrimPartPy[x]) + np.square(eventTree.truePrimPartPz[x])
            kE = eventTree.truePrimPartE[x] - np.sqrt((np.square(eventTree.truePrimPartE[x])) - pVector)
            if kE >= 0.06:
                nProtons += 1
                protonPresent = True
                
    if protonPresent == False:
        continue

#fill histograms based on number of photons


print("There are " + str(trueFiducialCut) + " events cut by true fiducial")
print("There are " + str(trueCosmicCut) + " events cut by true cosmic")
print("There are " + str(trueCCcut) + " events cut by true cc")
print("There are " + str(recoFound) + " total events where reco found the vertex")