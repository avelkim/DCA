# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 20:36:51 2022

@author: Lounes
"""

#### PACKAGES ####
import csv
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import argparse


#### PARAMS DEF ######
aduToVolt = 20e-6   #METTRE A 1 SI L'ON VEUT UTILISER LES DONNEES BRUTES DES ADCs
gain = 8
#### FUNCTIONS DEF ####

def help():
	print("Functions list:\n\n \
	getData(xlsFile, channelNbr, startPoint=0) \n \
		returns (channelData*aduToVolt/gain, nbrSamples) \n\n \
	plotData(xlsFile, channelNbr, startPoint=0) \n \
		plot DATA and returns mean \n\n \
	getDataRms(xlsFile, channelNbr, startPoint=0) \n \
		returns RMS value \n\n \
	getDataAverage(xlsFiles, channelNbr, startPoint=0)\n \
		returns average/nbrOfXlsFiles \n\n \
	getDataAverageRms(xlsFiles, channelNbr, startPoint=0) \n \
		returns RMS value \n\n \
	getPsd(xlsFile, channelNumber, samplingFrequency, startPoint=0) \n \
		returns (PSD, channelData.size) \n\n \
	plotPsd(xlsFile, channelNumber, samplingFrequency, startPoint=0, xScale='log', yScale='log', labelName='PSD') \n \
		plot PSD \n\n " )
		


## Return CHANNEL DATA from xls file and its LENGTH
def getData(xlsFile, channelNbr, startPoint=0):            
    with open(xlsFile, 'r') as file:                # Open then read csv
        reader = csv.reader(file, delimiter ='\t')
        rows = list(reader)
        
    nbrSamples = int(int(rows[47][1])/4)-startPoint            # NumberAdcDataNumb/4
    channelData = np.zeros(nbrSamples)

    for i in range(nbrSamples):                     # Fill channelData
        channelData[i] = int(rows[49+i+startPoint][channelNbr])
        
    file.close()                                    
    return channelData*aduToVolt/gain, nbrSamples

    

## Plot CHANNEL DATA from xls file
def plotData(xlsFile, channelNbr, startPoint=0, labelName="Raw data"):
    channelData = getData(xlsFile, channelNbr, startPoint)[0]
    plt.plot(channelData, label="Channel "+str(channelNbr)+" raw data.")
    plt.legend()
    plt.xlabel("Sample index")
    plt.ylabel("Input-referred noise amplitude (V)")
    return np.mean(channelData)


def getRms(xlsFile, channelNbr, startPoint=0):
    channelData = getData(xlsFile, channelNbr, startPoint)[0]
    print(np.std(channelData))
    return np.std(channelData)

def getGain(xlsFile, channelNbr, inputValue, startPoint=0):
    channelData = getData(xlsFile, channelNbr, startPoint)[0]
    diff=0
    for i in range(channelData.size):
        diff += channelData[i]*(-1)**i
    return np.abs(diff*gain/inputValue/(channelData.size/2))

'''
def getDataAverage(xlsFiles, channelNbr, startPoint=0):
    devideBy = len(xlsFiles)    
    
    init = getData(xlsFiles[0], channelNbr, startPoint)
    size = init[0].size
    
    for i in range (1, devideBy):
        D = getData(xlsFiles[i], channelNbr, startPoint)
        if (size>D[1]):
            size = D[1]    
    
    average = init[0][:size]
    for i in range (1, devideBy):
       D = getData(xlsFiles[i], channelNbr, startPoint)
       average = average + D[0][:size]
    return average/devideBy
'''   
    

## Return the Power Spectral Density
def getNasd(xlsFile, channelNumber, samplingFrequency, startPoint=0):
    channelData = getData(xlsFile, channelNumber, startPoint)[0]
    PSD = scipy.signal.periodogram(channelData, samplingFrequency)
    return PSD, channelData.size


## Plot NASD 
def plotNasd(xlsFile, channelNumber, samplingFrequency, startPoint=0, xScale='log', yScale='log', labelName='NASD'):
    PSD = getNasd(xlsFile, channelNumber, samplingFrequency, startPoint)
    print('RMS Value: ',np.sqrt(np.sum(PSD[0][1]))*np.sqrt(samplingFrequency/(PSD[1])))
    plt.plot(PSD[0][0][1:], np.sqrt(PSD[0][1][1:]), label=labelName)
    plt.legend()
    plt.xscale(xScale)
    plt.yscale(yScale)
    

## affiche la trace de la moyenne du NSD à partir d'une liste de fichiers XLS en entrée
def getNasdAverage(xlsFiles, channelNbr, samplingFrequency, startPoint=0):
    divideBy = len(xlsFiles)    
    
    init = getData(xlsFiles[0], channelNbr, startPoint)
    size = init[0].size
    
    for i in range (1, divideBy):
        D = getData(xlsFiles[i], channelNbr, startPoint)
        if (size>D[1]):
            size = D[1]    
    
    psdAverage = scipy.signal.periodogram(init[0][:size], samplingFrequency)[1]
    
    for i in range (1, divideBy):
        D = getData(xlsFiles[i], channelNbr, startPoint)
        PSD = scipy.signal.periodogram(D[0][:size], samplingFrequency)
        psdAverage = psdAverage + PSD[1]
    return PSD[0], psdAverage/divideBy, size 
        

def plotNasdAverage(xlsFiles, channelNumber, samplingFrequency, startPoint=0, xScale='log', yScale='log', labelName='NASD averaged over 5 acquisitions'):
    PSD = getNasdAverage(xlsFiles, channelNumber, samplingFrequency, startPoint)
    print('RMS value: ', np.sqrt(np.sum(PSD[1]))*np.sqrt(samplingFrequency/(PSD[2])))
    plt.plot(PSD[0][1:], np.sqrt(PSD[1][1:]), label=labelName)
    plt.legend()
    plt.xscale(xScale)
    plt.yscale(yScale)
    plt.xlabel("Frequency(Hz)")
    plt.ylabel("Noise Amplitude Spectral Density(V/√Hz)")




def main():
        parser = argparse.ArgumentParser(description='Parse through arguments')
        parser.add_argument('--action', '-a', required=True, type=str, help='Choose to get a value or to plot a graph \n')
        parser.add_argument('--file', '-f', required=True, type=str, nargs='*', help='One or more files (for average)\n')
        parser.add_argument('--gain', '-g', required=True, type=float, help='Choose your gain\n')
        parser.add_argument('--aduToVolt', '-aduToVolt', required=True, type=float, help='Convert your raw data in ADU to Volts\n')
        parser.add_argument('--samplingFrequency', '-freq', required=False, type=float, help='The sampling frequency\n')
        parser.add_argument('--channelNumber', '-c', required=True, type=int, help='Choose your channel number\n')
        parser.add_argument('--inputSignal', '-input', required=False, type=float, help='Amplitude of your input signal\n')
        parser.add_argument('--start', '-s', required=False, type=int, help='The starting point from which data processing starts\n')
        parser.add_argument('--xScale', '-x', required=False, type=str, help='Choose your axis scaling\n')
        parser.add_argument('--yScale', '-y', required=False, type=str, help='Choose your axis scaling\n')

        
        args = parser.parse_args()
        
        dcaAction = args.action
        dcaFiles = args.file
        dcaSampFreq = 0 if args.samplingFrequency==None else args.samplingFrequency
        global gain 
        gain = args.gain
        global aduToVolt 
        aduToVolt = args.aduToVolt
        inputSignal = args.inputSignal
        dcaChannelNumber = args.channelNumber
        dcaStartPoint= 0 if args.start==None else args.start
        x = 'linear' if args.xScale==None else args.xScale
        y = 'linear' if args.yScale==None else args.yScale

       
       
        if dcaAction == 'plotData':
                plotData(dcaFiles[0], dcaChannelNumber, dcaStartPoint)
                plt.show()  
                
                          
        if dcaAction == 'getRms':
                getRms(dcaFiles[0], dcaChannelNumber, dcaStartPoint)
                
                                
        if dcaAction == 'getGain':
                plotPsd(dcaFiles[0], dcaChannelNumber, inputSignal,dcaStartPoint)
                
                
        if dcaAction == 'plotNasd':
                if (len(dcaFiles) == 1):
                        plotNasd(dcaFiles[0], dcaChannelNumber, dcaSampFreq, dcaStartPoint, xScale=x, yScale=y)
                        plt.show()
                if (len(dcaFiles) > 1):
                        plotNasdAverage(dcaFiles, dcaChannelNumber, dcaSampFreq, dcaStartPoint, xScale=x, yScale=y)
                        plt.show()
                
              
                




if __name__=='__main__':
        main()

