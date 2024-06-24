import sys, argparse
import numpy as np
import ROOT as rt

from helpers.larflowreco_ana_funcs import getCosThetaGravVector

parser = argparse.ArgumentParser("Make energy histograms from a bnb nu overlay ntuple file")
parser.add_argument("-i", "--infile", type=str, required=True, help="input ntuple file")
parser.add_argument("-o", "--outfile", type=str, default="example_ntuple_analysis_script_output.root", help="output root file name")
parser.add_argument("-fc", "--fullyContained", action="store_true", help="only consider fully contained events")
parser.add_argument("-ncc", "--noCosmicCuts", action="store_true", help="don't apply cosmic rejection cuts")
args = parser.parse_args()

# needed for proper scaling of error bars:
#rt.TH1.SetDefaultSumw2(rt.kTRUE)

#open input file and get event and POT trees
ntuple_file = rt.TFile(args.infile)
eventTree = ntuple_file.Get("EventTree")
potTree = ntuple_file.Get("potTree")

#we will scale histograms to expected event counts from POT in runs 1-3: 6.67e+20
targetPOT = 6.67e+20
targetPOTstring = "6.67e+20" #for plot axis titles

#calculate POT represented by full ntuple file after applying cross section weights
ntuplePOTsum = 0.
for i in range(potTree.GetEntries()):
    potTree.GetEntry(i)
    ntuplePOTsum = ntuplePOTsum + potTree.totGoodPOT

#define histograms to fill
#we will write histograms to output file for:
protonGammaHist = rt.TH1F("twoPhotonHist", "Energy of NC events with photons and protons",60,0,6)

# set histogram axis titles and increase line width
def configureHist(h):
    h.GetYaxis().SetTitle("events per "+targetPOTstring+" POT")
    h.GetXaxis().SetTitle("energy (GeV)")
    h.SetLineWidth(2)
    return h

#scale the histogram based on total good POT
protonGammaHist = configureHist(protonGammaHist)

#set detector min/max and fiducial width (cm)
xMin, xMax = 0, 256
yMin, yMax = -116.5, 116.5
zMin, zMax = 0, 1036
fiducialWidth = 10

#begin loop over events in ntuple file
for i in range(eventTree.GetEntries()):
    eventTree.GetEntry(i)

#cut CC events
    if eventTree.trueNuCCNC != 1:
        continue

#cut everything within fiducialWidth of detector wall
    if eventTree.trueVtxX <= (xMin + fiducialWidth) or eventTree.trueVtxX >= (xMax - fiducialWidth) or \
        eventTree.trueVtxY <= (yMin + fiducialWidth) or eventTree.trueVtxY >= (yMax - fiducialWidth) or \
        eventTree.trueVtxZ <= (zMin + fiducialWidth) or eventTree.trueVtxZ >= (zMax - fiducialWidth):
        continue
        
#cut out cosmics: this cuts events tagged as overlapping w/cosmics
#NTS: will need algorithm for this when using reco/real data - upping fiducial to 12-13cm
#seems like the way to go re: assuring cosmics are cut
    if eventTree.vtxFracHitsOnCosmic >= 1.:
        continue
  
#determine whether there are photons as secondary particles
    photonInSecondary = False
    primList = []
    pionPresent = False
    protonPresent = False
#check if Neutral Pion and Kaon in primaries - must be a photon if so
    if 111 in eventTree.truePrimPartPDG or 311 in eventTree.truePrimPartPDG:
        photonInSecondary = True
    else:
  #Create a list of prime particle Track IDs
        for x in range(len(eventTree.trueSimPartTID)):
            if eventTree.trueSimPartTID[x] == eventTree.trueSimPartMID[x]:
                primList.append(eventTree.trueSimPartTID[x])
  #Iterate through to find photons
        for x in range(len(eventTree.trueSimPartPDG)):
            if eventTree.trueSimPartPDG[x] == 22:
  #Check for parent particle in the primary list
                if eventTree.trueSimPartMID[x] in primList:
                    photonInSecondary = True
  #Check if the photon has coordinates exactly equal to that of the event vertex
                if abs(eventTree.trueSimPartX[x] - eventTree.trueVtxX) <= 0.15 and abs(eventTree.trueSimPartY[x] - eventTree.trueVtxY) <= 0.15 and abs(eventTree.trueSimPartZ[x] -eventTree.trueVtxZ) <= 0.15:
                    photonInSecondary = True
  #Discard event unless a secondary photon is found
    if photonInSecondary == False:
        continue

  #HERE IS WHERE WE WILL DIVIDE THE EVENTS INTO BINS

  #Determining presence of suitably energetic protons and pions
    for x in range(len(eventTree.truePrimPartPDG)):
        if eventTree.truePrimPartPDG[x] == 211 and eventTree.truePrimPartE[x] >= 0.03:
            pionPresent = True
        elif eventTree.truePrimPartPDG[x] == 2212 and eventTree.truePrimPartE[x] >= 0.06:
            protonPresent = True
      
  #Now we sort
    if protonPresent == True and pionPresent == False:
        protonGammaHist.Fill(eventTree.trueNuE, eventTree.xsecWeight)  
    else:
        continue
      
#----- end of event loop ---------------------------------------------#

#scale histograms to target POT
protonGammaHist.Scale(targetPOT/ntuplePOTsum)

#create output root file and write histograms to file
outFile = rt.TFile(args.outfile, "RECREATE")
protonGammaHist.Write()