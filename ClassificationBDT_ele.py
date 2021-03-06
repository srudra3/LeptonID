#!/usr/bin/env python
from ROOT import TMVA, TFile, TTree, TCut, TChain
from subprocess import call
from os.path import isfile
from array import array
from math import *
#from LatinoAnalysis.NanoGardener.modules.GenLeptonMatchProducer import GenLeptonMatchProducer
#from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
#from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

# Setup TMVA
def runJob():
    TMVA.Tools.Instance()
    TMVA.PyMethodBase.PyInitialize()

    dataloader = TMVA.DataLoader('dataset_el')
    output = TFile.Open('TMVA_lep_el_prompt.root', 'RECREATE')
    factory = TMVA.Factory('TMVAClassification', output,'!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification')
                  
#    inputS = TFile.Open("root://cms-xrd-global.cern.ch///store/mc/RunIIFall17NanoAODv5/DYJetsToLL_M-5to50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/773DAD3C-8145-F643-8934-ACEFB018C1D6.root")
#    inputB = TFile.Open("root://cms-xrd-global.cern.ch///store/mc/RunIIFall17NanoAODv5/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/59A3A9A4-660B-7B4F-B858-23CFE7C09303.root")
    inputS = TFile.Open("/afs/cern.ch/work/s/srudrabh/ZH3l/CMSSW_10_2_0/src/LatinoAnalysis/NanoGardener/test/DYJetsToLL_M-50_v7_ElePromptGenMatched.root")
    inputBA = TFile.Open("/afs/cern.ch/work/s/srudrabh/ZH3l/CMSSW_10_2_0/src/LatinoAnalysis/NanoGardener/test/WJetsToLNu_v7_ElePromptGenMatched.root")
    inputBB = TFile.Open("/afs/cern.ch/work/s/srudrabh/ZH3l/CMSSW_10_2_0/src/LatinoAnalysis/NanoGardener/test/TTToSemiLeptonic_v7_ElePromptGenMatched.root") 
    signalTree = inputS.Get("Events")
    backgroundTreeA = inputBA.Get("Events")
    backgroundTreeB = inputBB.Get("Events")
    #Filling mvaVariables to the Factory-- implicit Event loop
    dataloader.AddVariable("Electron_pt", "Electron_pt",'F')
    dataloader.AddVariable("Electron_eta", "Electron_eta",'F')
#    dataloader.AddVariable("Electron_miniPFRelIso_chg", "Electron_miniPFRelIso_chg", 'F')
#    dataloader.AddVariable("Electron_miniPFRelIso_neu := Electron_miniPFRelIso_all-Electron_miniPFRelIso_chg", "Electron_miniPFRelIso_neu", 'F')
    dataloader.AddVariable("Electron_miniPFRelIso_all", "Electron_miniPFRelIso_all", 'F')
    dataloader.AddVariable("Electron_r9", "Electron_r9", 'F')
    dataloader.AddVariable("Dxy_electron := log(abs(Electron_dxy))", "Dxy_electron", 'F')
    dataloader.AddVariable("Dz_electron := log(abs(Electron_dz))", "Dz_electron", 'F')
    dataloader.AddVariable("Electron_sip3d", "Electron_sip3d", 'F')
    dataloader.AddVariable("Electron_convVeto", "Electron_convVeto", 'F')
    dataloader.AddVariable("Electron_lostHits", "Electron_lostHits", 'F')
    dataloader.AddVariable("Electron_mvaFall17V2noIso", "Electron_mvaFall17V2noIso", 'F')
    dataloader.AddVariable("BtagDeepFlavB_jet := (Electron_jetIdx >= 0)*(Jet_btagDeepFlavB[max(Electron_jetIdx,0)])", "BtagDeepFlavB_jet", 'F') #takes a non-zero value only when there are associated jets i.e;Electron_jetIdx>=0
    dataloader.AddVariable("JetPtRelv2_electron := (Electron_jetIdx >= 0)*(Electron_jetPtRelv2)", "JetPtRelv2_electron", 'F') #takes a non-zero value only when there are associated jets 
    dataloader.AddVariable("Electron_jetPtRatio := (Electron_jetIdx == -1)*((1)/(1+(Electron_miniPFRelIso_all)))+ (Electron_jetIdx >= 0)*((Electron_pt)/(Jet_pt[max(Electron_jetIdx,0)]))", "Electron_jetPtRatio", 'F') #proxy for jet pt when no associated jets found
    signalWeight = 1.0
    backgroundWeight = 1.0

    dataloader.AddSignalTree(signalTree, signalWeight)
    dataloader.AddBackgroundTree(backgroundTreeA, backgroundWeight)
    dataloader.AddBackgroundTree(backgroundTreeB, backgroundWeight)
    dataloader.SetSignalWeightExpression("Electron_promptgenmatched")
    dataloader.SetBackgroundWeightExpression("!Electron_promptgenmatched")
    mycuts = TCut("Electron_pt>15")
    mycutb = TCut("Electron_pt>15")

    dataloader.PrepareTrainingAndTestTree(mycuts, mycutb,'nTrain_Signal=0:nTrain_Background=0:nTest_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V') 
    factory.BookMethod(dataloader, TMVA.Types.kBDT, "BDT", "!H:!V:NTrees=500:MinNodeSize=0.5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.1:SeparationType=GiniIndex:nCuts=500" );
    factory.BookMethod(dataloader, TMVA.Types.kBDT, "BDTG", "!H:!V:NTrees=500:MinNodeSize=0.5%:MaxDepth=3:BoostType=Grad:Shrinkage=0.05:UseBaggedBoost:GradBaggingFraction=0.5:nCuts=500" ); 
    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    output.Close()
if __name__ == "__main__":
    runJob()
