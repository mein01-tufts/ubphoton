import sys, argparse
import numpy as np
import ROOT as rt
rt.PyConfig.IgnoreCommandLineOptions = True
rt.gROOT.SetBatch(True)

from cuts import trueCutNC, trueCutFiducials,trueCutCosmic, truePhotonList, trueCutPionProton, histStack, recoNoVertex, recoFiducials, recoPhotonList, recoPionProton, recoNeutralCurrent, scaleRecoEnergy, scaleTrueEnergy, recoPion, recoProton, recoCutShowerFromChargeScore, recoCutLongTracks, recoPhotonListFiducial, recoCutPrimary, recoCutShortTracks, recoPhotonListTracks, recoCutFarShowers, trueCutMuons, trueCutElectrons, recoCutMuons, recoCutElectrons, recoCutManyTracks, recoCutCompleteness, recoCutMuonCompleteness

from helpers.larflowreco_ana_funcs import getCosThetaGravVector

parser = argparse.ArgumentParser("Make energy histograms from a bnb nu overlay ntuple file")
parser.add_argument("-i", "--infile", type=str, required=True, help="input ntuple file")
parser.add_argument("-o", "--outfile", type=str, default="example_ntuple_analysis_script_output.root", help="output root file name")
parser.add_argument("-fc", "--fullyContained", action="store_true", help="only consider fully contained events")
parser.add_argument("-ncc", "--noCosmicCuts", action="store_true", help="don't apply cosmic rejection cuts")

args = parser.parse_args()

#open input file and get event and POT trees
ntuple_file = rt.TFile(args.infile)
eventTree = ntuple_file.Get("EventTree")
potTree = ntuple_file.Get("potTree")

#we will scale histograms to expected event counts from POT in runs 1-3: 6.67e+20
targetPOT = 6.67e+20
targetPOTstring = "6.67e+20"
ntuplePOTsum = 0

for i in range(potTree.GetEntries()):
  potTree.GetEntry(i)
  ntuplePOTsum = ntuplePOTsum + potTree.totGoodPOT

cosmicPOTsum = 3.2974607516739725e+20

#Hists created and organized here
#PURITY HISTOGRAMS
puritySignal1 =  rt.TH1F("PSignal1", "Signal",60,0,2)
#purityCC1 = rt.TH1F("PCC1", "Actually Charged Current",60,0,2)
purityMuon1 = rt.TH1F("PMuon1", "Over-threshold Muon",60,0,2)
purityElectron1 = rt.TH1F("PElectron1", "Over-threshold Electron",60,0,2)
purityFiducials1 = rt.TH1F("PFiducial1", "Out of Fiducial",60,0,2)
purityPionProton1 = rt.TH1F("PPionProton1", "Charged Pion or Proton",60,0,2)
purityNoPhotons1 = rt.TH1F("PNoPhoton1", "No Real Photons",60,0,2)
purityTwoPhotons1 = rt.TH1F("PTwoPhoton1", "2 Real Photons",60,0,2)
purityManyPhotons1 = rt.TH1F("PMorePhoton1", "3+ Real Photons",60,0,2)

puritySignal2 =	 rt.TH1F("PSignal2", "Signal",60,0,2)
#purityCC2 = rt.TH1F("PCC2", "Actually Charged Current",60,0,2)
purityMuon2 = rt.TH1F("PMuon2", "Over-threshold Muon",60,0,2)
purityElectron2 = rt.TH1F("PElectron2", "Over-threshold Electron",60,0,2)
purityFiducials2 = rt.TH1F("PFiducial2", "Out of Fiducial",60,0,2)
purityPionProton2 = rt.TH1F("PPionProton2", "Charged Pion or Proton",60,0,2)
purityNoPhotons2 = rt.TH1F("PNoPhoton2", "No Real Photons",60,0,2)
purityOnePhoton2 = rt.TH1F("POnePhoton2", "1 Real Photon",60,0,2)
purityManyPhotons2 = rt.TH1F("PManyPhoton2", "3+ Real Photons",60,0,2)

puritySignal3 =	 rt.TH1F("PSignal3", "Signal",60,0,2)
#purityCC3 = rt.TH1F("PCC3", "Actually Charged Current",60,0,2)
purityMuon3 = rt.TH1F("PMuon3", "Over-threshold Muon",60,0,2)
purityElectron3 = rt.TH1F("PElectron3", "Over-threshold Electron",60,0,2)
purityFiducials3 = rt.TH1F("PFiducial3", "Out of Fiducial",60,0,2)
purityPionProton3 = rt.TH1F("PPionProton3", "Charged Pion or Proton",60,0,2)
purityNoPhotons3 = rt.TH1F("PNoPhoton3", "No Real Photons",60,0,2)
purityOnePhoton3 = rt.TH1F("POnePhoton3", "2 Real Photons",60,0,2)
purityTwoPhotons3 = rt.TH1F("PTwoPhotons33", "3+ Real Photons",60,0,2)

#PURITY HISTLISTS
signalPHists = [puritySignal1, puritySignal2, puritySignal3]
#CCPHists = [purityCC1, purityCC2, purityCC3]
muonPHists = [purityMuon1, purityMuon2, purityMuon3]
electronPHists = [purityElectron1, purityElectron2, purityElectron3]
fiducialPHists = [purityFiducials1, purityFiducials2, purityFiducials3]
pionProtonPHists = [purityPionProton1, purityPionProton2, purityPionProton3]
noPhotonPHists = [purityNoPhotons1, purityNoPhotons2, purityNoPhotons3]
onePhotonPHists = [puritySignal1, purityOnePhoton2, purityOnePhoton3]
twoPhotonPHists = [purityTwoPhotons1, puritySignal2, purityTwoPhotons3]
manyPhotonPHists = [purityManyPhotons1, purityManyPhotons2, puritySignal3]

#Cosmics go here, so we can put them on purity
cosmicOnePhoton = rt.TH1F("cBackground1", "Cosmic Background",60,0,2)
cosmicTwoPhotons = rt.TH1F("cBackground2", "Cosmic Background",60,0,2)
cosmicThreePhotons = rt.TH1F("cBackground3", "Cosmic Background",60,0,2)
cosmicList = [cosmicOnePhoton, cosmicTwoPhotons, cosmicThreePhotons]
cosmicThreshold = rt.TH1F("cosmicThreshold", "Necessary Signal to Beat Cosmics (Single Photon)",60,0,2)

#Big Lists, for Big Plots
pList1 = [puritySignal1, purityMuon1, purityElectron1, purityFiducials1, purityPionProton1, purityNoPhotons1, purityTwoPhotons1, purityManyPhotons1, cosmicOnePhoton]
pList2 = [puritySignal2, purityMuon2, purityElectron2, purityFiducials2, purityPionProton2, purityNoPhotons2, purityOnePhoton2, purityManyPhotons2, cosmicTwoPhotons] 
pList3 = [puritySignal3, purityMuon3, purityElectron3, purityFiducials3, purityPionProton3,	purityNoPhotons3, purityOnePhoton3, purityTwoPhotons3, cosmicThreePhotons]


#EFFICIENCY HISTOGRAMS
effTotal1 = rt.TH1F("effTotal1", "One Photon",60,0,2)
effNoVertex1 = rt.TH1F("effNoVertex1", "No Vertex Found",60,0,2)
#effCC1 = rt.TH1F("effCC1", "CC False Positive",60,0,2)
effMuon1 = rt.TH1F("effMuon1", "Muon False Positive",60,0,2)
effElectron1 = rt.TH1F("effElectron1", "Electron False Positive",60,0,2)
effFiducial1 = rt.TH1F("effFiducial1", "Placed out of Fiducial",60,0,2)
effPion1 = rt.TH1F("effPion1", "Pion False Positive",60,0,2)
effProton1 =  rt.TH1F("effProton1", "Proton False Positive",60,0,2)
effNoPhotons1 = rt.TH1F("effNoPhotons1", "No Photons Found",60,0,2)
effSignal1 = rt.TH1F("effSignal 1", "Signal",60,0,2)
effTwoPhotons1 = rt.TH1F("effTwoPhotons1", "Two Photons Found",60,0,2)
effManyPhotons1 = rt.TH1F("effManyPhotons1", "Many Photons Found",60,0,2)
effShowerCharge1 = rt.TH1F("effShowerCharge1", "Shower from Charged Cut",60,0,2)
effPrimary1 = rt.TH1F("effPrimary1", "Primary Score Cut",60,0,2)
effLongTracks1 = rt.TH1F("effLongTracks1", "Tracks with length > 20 cm",60,0,2)
effMuonComp1 = rt.TH1F("effMuonComp1", "Muons with too-low Efficiency",60,0,2)

effTotal2 = rt.TH1F("effTotal2", "Two Photons",60,0,2)
effNoVertex2 = rt.TH1F("effNoVertex2", "No Vertex Found",60,0,2)
#effCC2 = rt.TH1F("effCC2", "CC False Positive",60,0,2)
effMuon2 = rt.TH1F("effMuon2", "Muon False Positive",60,0,2)
effElectron2 = rt.TH1F("effElectron2", "Electron False Positive",60,0,2)
effFiducial2 = rt.TH1F("effFiducial2", "Placed out of Fiducial",60,0,2)
effPion2 = rt.TH1F("effPion2", "Pion False Positive",60,0,2)
effProton2 =  rt.TH1F("effProton2", "Proton False Positive",60,0,2)
effNoPhotons2 =	rt.TH1F("effNoPhotons2", "No Photons Found",60,0,2)
effSignal2 = rt.TH1F("effSignal2", "Signal",60,0,2)
effOnePhoton2 = rt.TH1F("effOnePhoton2", "One Photon Found",60,0,2)
effManyPhotons2 = rt.TH1F("effManyPhotons2", "Many Photons Found",60,0,2)
effShowerCharge2 = rt.TH1F("effShowerCharge2", "Shower from Charged Cut",60,0,2)
effPrimary2 = rt.TH1F("effPrimary2", "Primary Score Cut",60,0,2)
effLongTracks2 = rt.TH1F("effLongTracks2", "Tracks with length > 20 cm",60,0,2)
effMuonComp2 = rt.TH1F("effMuonComp2", "Muons with too-low Efficiency",60,0,2)


effTotal3 = rt.TH1F("effTotal3", "3+ Photons",60,0,2)
effNoVertex3 = rt.TH1F("effNoVertex3", "No Vertex Found",60,0,2)
#effCC3 = rt.TH1F("effCC3", "CC False Positive",60,0,2)
effMuon3 = rt.TH1F("effMuon3", "Muon False Positive",60,0,2)
effElectron3 = rt.TH1F("effElectron3", "Electron False Positive",60,0,2)
effFiducial3 = rt.TH1F("effFiducial3", "Placed out of Fiducial",60,0,2)
effPion3 = rt.TH1F("effPion3", "Pion False Positive",60,0,2)
effProton3 =  rt.TH1F("effProton3", "Proton False Positive",60,0,2)
effNoPhotons3 =	rt.TH1F("effNoPhotons3", "No Photons Found",60,0,2)
effSignal3 = rt.TH1F("effSignal 3", "Signal",60,0,2)
effOnePhoton3 = rt.TH1F("effManyPhotons3", "Many Photons Found",60,0,2)
effTwoPhotons3 = rt.TH1F("effTwoPhotons3", "Two Photons Found",60,0,2)
effShowerCharge3 = rt.TH1F("effShowerCharge3", "Shower from Charged Cut",60,0,2)
effPrimary3 = rt.TH1F("effPrimary3", "Primary Score Cut",60,0,2)
effLongTracks3 = rt.TH1F("effLongTracks3", "Tracks with length > 20 cm",60,0,2)
effCompleteness3 = rt.TH1F("effCompleteness3", "Showers with completeness below 0.3",60,0,2)
effMuonComp3 = rt.TH1F("effMuonComp3", "Muons with too-low Efficiency",60,0,2)

#Histogram Lists!
effTotalList = [effTotal1, effTotal2, effTotal3]
effNoVertexHists = [effNoVertex1, effNoVertex2, effNoVertex3]
#effCCHists = [effCC1, effCC2, effCC3]
effMuonHists = [effMuon1, effMuon2, effMuon3]
effElectronHists = [effElectron1, effElectron2, effElectron3]
effFiducialHists = [effFiducial1, effFiducial2, effFiducial3]
effPionHists = [effPion1, effPion2, effPion3]
effProtonHists = [effProton1, effProton2, effProton3]
effNoPhotonHists = [effNoPhotons1, effNoPhotons2, effNoPhotons3]
effOnePhotonHists = [effSignal1, effOnePhoton2, effOnePhoton3] 
effTwoPhotonHists = [effTwoPhotons1, effSignal2, effTwoPhotons3]
effManyPhotonHists = [effManyPhotons1, effManyPhotons2, effSignal3]
effShowerChargeHists = [effShowerCharge1, effShowerCharge2, effShowerCharge3]
effLongTrackHists = [effLongTracks1, effLongTracks2, effLongTracks3]
effPrimaryHists = [effPrimary1, effPrimary2, effPrimary3]
effMuonCompHists = [effMuonComp1, effMuonComp2, effMuonComp3]

#Lists of histograms for stacking. Place with signal first, then put the others in backwards in order of application (so the last one to apply would immediately follow the signal, then the second to last, all the way down to the first)
effList1 = [effSignal1, effMuonComp1, effLongTracks1, effPrimary1, effManyPhotons1, effTwoPhotons1, effNoPhotons1, effShowerCharge1, effProton1, effPion1, effElectron1, effMuon1, effNoVertex1]
effList2 = [effSignal2, effMuonComp2, effLongTracks2, effPrimary2, effManyPhotons2, effOnePhoton2, effNoPhotons2, effShowerCharge2, effProton2, effPion2, effElectron2, effMuon2, effNoVertex2]
effList3 = [effSignal3, effMuonComp3, effLongTracks3, effPrimary3, effTwoPhotons3, effOnePhoton3, effNoPhotons3, effShowerCharge3, effProton3, effPion3, effElectron3, effMuon3, effNoVertex3]


#Built-in functions here
def addHist(ntuple, photonList, photonList2, histList, variable, weight):
  if len(photonList) + len(photonList2) == 1:
    histList[0].Fill(variable, weight)
  elif len(photonList) + len(photonList2) == 2:
    histList[1].Fill(variable, weight)
  else:
    histList[2].Fill(variable, weight)


def histScale(hist, POTSum):
  POTTarget = 6.67e+20
  hist.Scale(POTTarget/POTSum)
  return hist

#Variables for program review
initialCount = 0
vertexCount = 0
NCCount = 0
fiducialCount = 0
noPionCount = 0
recoCount = 0
onePhoton = 0
twoPhotons = 0
threePhotons = 0
count = 0

totalCosmics = 0
vertexCosmics = 0 
NCCosmics = 0
MattProofCosmics = 0
fiducialCosmics = 0
pionlessCosmics = 0
photonCosmics = 0
uncutCosmics = 0
untrackedCosmics = 0

passTruth = 0
hasVertex = 0
hasNC = 0
inFiducial = 0
pionProtonFine = 0
survivesCuts = 0
noEffPhotons = 0
oneEffPhoton = 0
twoEffPhotons = 0
manyEffPhotons = 0

#We put this into the addHist function for truth-based graphs
emptyList = []

#Variables for program function
fiducialData = {"xMin":0, "xMax":256, "yMin":-116.5, "yMax":116.5, "zMin":0, "zMax":1036, "width":30}
classificationThreshold = 0

#BEGINNING EVENT LOOP FOR DEFAULT PURITY
for i in range(eventTree.GetEntries()):
  eventTree.GetEntry(i)

  #Selecting events with reco
  #See if the event has a vertex
  if recoNoVertex(eventTree) == False:
    continue

  #See if the event is neutral current
  if recoCutMuons(eventTree, classificationThreshold) == False:
    continue

  if recoCutElectrons(eventTree, classificationThreshold) == False:
    continue

  #Use Matt's Cosmic Cut
  if trueCutCosmic(eventTree) == False:
    continue

  #Make sure the event is within the fiducial volume
  if recoFiducials(eventTree, fiducialData) == False:
    continue

  #Cut events with suitably energetic charged pions 
  if recoPion(eventTree, classificationThreshold) == False:
    continue

  #Cut events with far-travelling protons
  recoProtonCount = recoProton(eventTree, classificationThreshold)
  if recoProtonCount > 1:
    continue

  #See if there are any photons in the event - if so, list them
  recoList = recoPhotonListFiducial(fiducialData, eventTree, classificationThreshold)

  #List all photons classified as tracks
  recoTrackList = recoPhotonListTracks(fiducialData, eventTree, classificationThreshold)

  if len(recoList) + len(recoTrackList) == 0:
    continue

  #Try cutting based on data for Shower from Charged
  if recoCutShowerFromChargeScore(eventTree, recoList, recoTrackList) == False:
    continue
  
  #Cut based on primary score
  if recoCutPrimary(eventTree, recoList, recoTrackList) == False:
    continue

  #Cut based on the presence of tracks over 20 cm
  if recoCutLongTracks(eventTree, fiducialData) == False:
    continue

  #Cut based on the completeness of known Muons
  if recoCutMuonCompleteness(eventTree) == False:
    continue

  #PURITY - GRAPHING BASED ON TRUTH
  
  #Calculating graphing values
  leadingPhoton = scaleRecoEnergy(eventTree, recoList, recoTrackList)

  #Neutral current!
  #if trueCutNC(eventTree) == False:
  #  addHist(eventTree, recoList, recoTrackList, CCPHists, leadingPhoton, eventTree.xsecWeight)
  #  continue

  #Cut muons and electrons
  if trueCutMuons(eventTree) == False:
    muonInfoString = ("File ID:" + str(eventTree.fileid) + ", Run:" + str(eventTree.run) + ", Subrun:" + str(eventTree.subrun) + ", Event: " + str(eventTree.event) + ", Vertex Location (x,y,z): (" + str(eventTree.trueVtxX) + "," + str(eventTree.trueVtxY) + "," + str(eventTree.trueVtxZ) + ")\n")
    
    outFile = open("MuonFile.txt", "a")
    outFile.write(muonInfoString)
    outFile.close()