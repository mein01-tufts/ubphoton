# The following program is Matt Rosenberg's example script
# Adding in this repo for facility of reference

import sys, argparse
import numpy as np
import ROOT as rt

from helpers.larflowreco_ana_funcs import getCosThetaGravVector

#This section sets the input arguments necessary to run the file
#-i sets the input file "infile"
#-o sets the name of the file the results will be written to
#-fc and -ncc are other arguments
parser = argparse.ArgumentParser("Make energy histograms from a bnb nu overlay ntuple file")
parser.add_argument("-i", "--infile", type=str, required=True, help="input ntuple file")
parser.add_argument("-o", "--outfile", type=str, default="example_ntuple_analysis_script_output.root", help="output root file name")
parser.add_argument("-fc", "--fullyContained", action="store_true", help="only consider fully contained events")
parser.add_argument("-ncc", "--noCosmicCuts", action="store_true", help="don't apply cosmic rejection cuts")
args = parser.parse_args()

#needed for proper scaling of error bars:
rt.TH1.SetDefaultSumw2(rt.kTRUE)

#open input file and get event and POT trees
#input files are structured as dictionaries, with keys EventTree and potTree 
#assigned to their respective values, which are ROOT trees
ntuple_file = rt.TFile(args.infile)
eventTree = ntuple_file.Get("EventTree")
potTree = ntuple_file.Get("potTree")

#we will scale histograms to expected event counts from POT in runs 1-3: 6.67e+20
targetPOT = 6.67e+20
targetPOTstring = "6.67e+20" #for plot axis titles

# calculate POT represented by full ntuple file after applying cross section weights
# TTree.GetEntries() option returns the amount of entries in the pre-specified tree
# For Loop that calculates the total POT in the full ntuple file
ntuplePOTsum = 0.
for i in range(potTree.GetEntries()):
  potTree.GetEntry(i)
  ntuplePOTsum = ntuplePOTsum + potTree.totGoodPOT

#define histograms to be filled
#we will write histograms to output file
# rt.TH1F takes necessary args: ()"fileName", "histogram title", # of bins, #x-min, #x-max)

#true neutrino energy in GeV
h = rt.TH1F("h_trueNuE","True Neutrino Energy",30,0,6)
h.GetYaxis().SetTitle("events")
h.GetXaxis().SetTitle("energy (GeV)")
h.SetLineWidth(2)

for i in range(eventTree.GetEntries()):

  eventTree.GetEntry(i)
  h.Fill(eventTree.trueNuE, eventTree.xsecWeight)

outFile = rt.TFile(args.outfile, "RECREATE")
h.Write()
