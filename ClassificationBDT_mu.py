#!/usr/bin/env python
from ROOT import TMVA, TFile, TTree, TCut, TChain
from subprocess import call
from os.path import isfile
from array import array
from math import *

# Setup TMVA
def runJob():
    TMVA.Tools.Instance()
    TMVA.PyMethodBase.PyInitialize()

    dataloader = TMVA.DataLoader('dataset_mu')
    output = TFile.Open('TMVA_lep_mu_prompt.root', 'RECREATE')
    factory = TMVA.Factory('TMVAClassification', output,'!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification')
                  
#    inputS = TFile.Open("root://cms-xrd-global.cern.ch///store/mc/RunIIFall17NanoAODv5/DYJetsToLL_M-5to50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/773DAD3C-8145-F643-8934-ACEFB018C1D6.root")
 #   inputB = TFile.Open("root://cms-xrd-global.cern.ch///store/mc/RunIIFall17NanoAODv5/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/59A3A9A4-660B-7B4F-B858-23CFE7C09303.root")
    inputS = TFile.Open("/afs/cern.ch/work/s/srudrabh/ZH3l/CMSSW_10_2_0/src/LatinoAnalysis/NanoGardener/test/DYJetsToLL_M-50_v7_MuPromptGenMatched.root")
    inputBA = TFile.Open("/afs/cern.ch/work/s/srudrabh/ZH3l/CMSSW_10_2_0/src/LatinoAnalysis/NanoGardener/test/WJetsToLNu_v7_MuPromptGenMatched.root")
    inputBB = TFile.Open("/afs/cern.ch/work/s/srudrabh/ZH3l/CMSSW_10_2_0/src/LatinoAnalysis/NanoGardener/test/TTToSemiLeptonic_v7_MuPromptGenMatched.root")
    signalTree = inputS.Get("Events")
    backgroundTreeA = inputBA.Get("Events")
    backgroundTreeB = inputBB.Get("Events")
    #Filling mvaVariables to the Factory-- implicit Event loop
    dataloader.AddVariable("Muon_pt", "Muon_pt",'F')
    dataloader.AddVariable("Muon_eta", "Muon_eta",'F')
    dataloader.AddVariable("Muon_miniPFRelIso_chg", "Muon_miniPFRelIso_chg", 'F')
    dataloader.AddVariable("Muon_miniPFRelIso_neu := Muon_miniPFRelIso_all-Muon_miniPFRelIso_chg", "Muon_miniPFRelIso_neu", 'F')
    dataloader.AddVariable("Muon_dxy := log(abs(Muon_dxy))", "Muon_dxy", 'F')
    dataloader.AddVariable("Muon_dz := log(abs(Muon_dz))", "Muon_dz", 'F')
    dataloader.AddVariable("Muon_sip3d", "Muon_sip3d", 'F')
    dataloader.AddVariable("Muon_tightId", "Muon_tightId", 'F')
    dataloader.AddVariable("Muon_segmentComp", "Muon_segmentComp", 'F')
    dataloader.AddVariable("Jet_btagDeepFlavB_Muon := (Muon_jetIdx >= 0)*(Jet_btagDeepFlavB[max(Muon_jetIdx,0)])", "Jet_btagDeepFlavB_Muon", 'F') #takes a non-zero value only when there are associated jets i.e;Electron_jetIdx>=0
    dataloader.AddVariable("Muon_jetPtRelv2 := (Muon_jetIdx >= 0)*(Muon_jetPtRelv2)", "Muon_jetPtRelv2", 'F') #takes a non-zero value only when there are associated jets i.e;Electron_jetIdx>=0
    dataloader.AddVariable("Muon_jetPtRatio := (Muon_jetIdx == -1)*((1)/(1+(Muon_miniPFRelIso_all)))+ (Muon_jetIdx >= 0)*((Muon_pt)/(Jet_pt[max(Muon_jetIdx,0)]))", "Muon_jetPtRatio", 'F') #proxy for when no associated jets found
 
    signalWeight = 1.0
    backgroundWeight = 1.0

    dataloader.AddSignalTree(signalTree, signalWeight)
    dataloader.AddBackgroundTree(backgroundTreeA, backgroundWeight)
    dataloader.AddBackgroundTree(backgroundTreeB, backgroundWeight)
    dataloader.SetSignalWeightExpression("Muon_promptgenmatched")
    dataloader.SetBackgroundWeightExpression("!Muon_promptgenmatched")
    mycuts = TCut("")
    mycutb = TCut("")

    dataloader.PrepareTrainingAndTestTree(mycuts, mycutb,'nTrain_Signal=0:nTrain_Background=0:nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V') 
    factory.BookMethod(dataloader, TMVA.Types.kBDT, "BDT", "!H:!V:NTrees=500:MinNodeSize=0.5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.1:SeparationType=GiniIndex:nCuts=500" )
    factory.BookMethod(dataloader, TMVA.Types.kBDT, "BDTG", "!H:!V:NTrees=500:MinNodeSize=0.5%:MaxDepth=3:BoostType=Grad:Shrinkage=0.05:UseBaggedBoost:GradBaggingFraction=0.5:nCuts=500" )
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    output.Close()
if __name__ == "__main__":
    runJob()
