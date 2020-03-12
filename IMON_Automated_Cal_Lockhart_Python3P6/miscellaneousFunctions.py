# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 10:50:11 2019

@author: v-stpur
"""
from chromaInstrument import ChromaMainframe
from statistics import mean
import timerThread
#GIT Version

class MiscellaneousFunctions(object):

#    def __init__(self, vregUnderTest, load):
    def __init__(self):
        
        self.vregUnderTest = timerThread.VregUnderTest
        self.Load          = timerThread.Load
        self.chroma        = ChromaMainframe(self.Load)

        self.chroma.add_channel(1, 80, "CC", "HI")
        self.chroma.add_channel(3, 80, "CC", "HI")
        self.chroma.add_channel(5, 80, "CC", "HI")
        self.chroma.add_channel(7, 80, "CC", "HI")
        self.chroma.add_channel(9, 80, "CC", "HI")
        
        self.gfxKcs         = float(timerThread.GfxKcs)
        self.cpuKcs         = float(timerThread.CPUKcs)
        self.memphyKcs      = float(timerThread.MemphyKcs)
        self.socKcs         = float(timerThread.SocKcs)
        self.gfxGain        = float(timerThread.GfxGain)
        self.cpuGain        = float(timerThread.CpuGain)
        self.memphyGain     = float(timerThread.MemphyGain)
        self.socGain        = float(timerThread.SocGain)
        self.gfxRimon       = float(timerThread.GfxRimon)
        self.cpuRimon       = float(timerThread.CpuRimon)
        self.memphyRimon    = float(timerThread.MemphyRimon)
        self.socRimon       = float(timerThread.SocRimon)
        self.lockHart       = timerThread.LockHartCB
        self.lowCurrentGFX  = timerThread.LowCurrentGFX
        
     
    def calculateCurrent(self, data):
        if self.vregUnderTest == "GFX":
#            return data * 1000.0 / (10.0 * 9.7 / 8.0)
            return data * 1000.0 / (self.gfxRimon * self.gfxKcs / self.gfxGain)
        elif self.vregUnderTest == "CPU":
#            return data * 1000.0 / (10.0 * 8.7 / 8.0)
            return data * 1000.0 / (self.cpuRimon * self.cpuKcs / self.cpuGain)
        elif self.vregUnderTest == "SOC":
#            return data * 1000.0 / (40.0 * 10.0 / 16.0)
            return data * 1000.0 / (self.socRimon * self.socKcs / self.socGain)
        elif self.vregUnderTest == "MEMPHY":
#            return data * 1000.0 / (40.0 * 10.0 / 16.0)
            return data * 1000.0 / (self.memphyRimon * self.memphyKcs / self.memphyGain)
        
    def readBackLoad(self):
            
        readBackLoad1 = self.chroma.channelArray[0].get_measured_current()
        readBackLoad3 = self.chroma.channelArray[1].get_measured_current()
        readBackLoad5 = self.chroma.channelArray[2].get_measured_current()
        readBackLoad7 = self.chroma.channelArray[3].get_measured_current()
        readBackLoad9 = self.chroma.channelArray[4].get_measured_current()
        if self.lockHart:
            if self.vregUnderTest == "GFX":
                readBackLoad = float(readBackLoad7) + float(readBackLoad9)
            elif self.vregUnderTest == "CPU":
                readBackLoad = float(readBackLoad7) + float(readBackLoad9) 
            elif self.vregUnderTest == "MEMIO" or self.vregUnderTest == "MEMPHY" or self.vregUnderTest == "SOC":
                readBackLoad = float(readBackLoad7)
        else:
            if self.vregUnderTest == "GFX":
                readBackLoad = float(readBackLoad7) + float(readBackLoad5) + float(readBackLoad9) + float(readBackLoad3) + float(readBackLoad1)
            elif self.vregUnderTest == "CPU":
                readBackLoad = float(readBackLoad7) + float(readBackLoad9) 
            elif self.vregUnderTest == "MEMIO" or self.vregUnderTest == "MEMPHY" or self.vregUnderTest == "SOC":
                readBackLoad = float(readBackLoad7)
            
        return readBackLoad
    
    def setChromaCurrent(self, load):
        
        chroma1Load = 0.0
        chroma3Load = 0.0
        chroma5Load = 0.0
        chroma7Load = 0.0
        chroma9Load = 0.0
        
        if self.lockHart:
            print ("Doing LockHart Board")
            if self.vregUnderTest == "GFX":
                chroma1Load = load / 2.0
                self.chroma.channelArray[4].set_load(chroma1Load)
                chroma3Load = load / 2.0
                self.chroma.channelArray[3].set_load(chroma3Load)
                
            elif self.vregUnderTest == "CPU":
                chroma7Load = load / 2.0
                self.chroma.channelArray[4].set_load(chroma7Load)
                chroma9Load = load / 2.0
                self.chroma.channelArray[3].set_load(chroma9Load)
            elif self.vregUnderTest == "MEMIO" or self.vregUnderTest == "MEMPHY"  or self.vregUnderTest == "SOC" :
                chroma7Load = load
                self.chroma.channelArray[3].set_load(chroma7Load)
        else:
            if self.vregUnderTest == "GFX":
                chroma1Load = load / 5.0
                self.chroma.channelArray[0].set_load(chroma1Load)
                chroma3Load = load / 5.0
                self.chroma.channelArray[1].set_load(chroma3Load)
                chroma5Load = load / 5.0
                self.chroma.channelArray[2].set_load(chroma5Load)
                chroma7Load = load / 5.0
                self.chroma.channelArray[3].set_load(chroma7Load)
                chroma9Load = load / 5.0
                self.chroma.channelArray[4].set_load(chroma9Load)
                chroma1Load = load / 5.0
            elif self.vregUnderTest == "CPU":
                chroma7Load = load / 2.0
                self.chroma.channelArray[3].set_load(chroma7Load)
                chroma9Load = load / 2.0
                self.chroma.channelArray[4].set_load(chroma9Load)
            elif self.vregUnderTest == "MEMIO" or self.vregUnderTest == "MEMPHY"  or self.vregUnderTest == "SOC" :
                chroma7Load = load
                self.chroma.channelArray[3].set_load(chroma7Load)

    def loadOn(self):
            
        if self.lockHart:
            if self.vregUnderTest == "GFX":
                self.chroma.channelArray[3].load_on()
                self.chroma.channelArray[4].load_on()
            elif self.vregUnderTest == "CPU":
                self.chroma.channelArray[3].load_on()
                self.chroma.channelArray[4].load_on()
            elif self.vregUnderTest == "MEMPHY"  or self.vregUnderTest == "SOC" :
                self.chroma.channelArray[3].load_on()
        else:
            if self.vregUnderTest == "GFX":
                self.chroma.channelArray[0].load_on()
                self.chroma.channelArray[1].load_on()
                self.chroma.channelArray[2].load_on()
                self.chroma.channelArray[3].load_on()
                self.chroma.channelArray[4].load_on()
            elif self.vregUnderTest == "CPU":
                self.chroma.channelArray[3].load_on()
                self.chroma.channelArray[4].load_on()
            elif self.vregUnderTest == "MEMPHY"  or self.vregUnderTest == "SOC" :
                self.chroma.channelArray[3].load_on()

    def loadOff(self):
             
        if self.lockHart:
            if self.vregUnderTest == "GFX":
                self.chroma.channelArray[3].load_off()
                self.chroma.channelArray[4].load_off()
            elif self.vregUnderTest == "CPU":
                self.chroma.channelArray[3].load_off()
                self.chroma.channelArray[4].load_off()
            elif self.vregUnderTest == "MEMPHY"  or self.vregUnderTest == "SOC" :
                self.chroma.channelArray[3].load_off()
        else:
            if self.vregUnderTest == "GFX":
                self.chroma.channelArray[0].load_off()
                self.chroma.channelArray[1].load_off()
                self.chroma.channelArray[2].load_off()
                self.chroma.channelArray[3].load_off()
                self.chroma.channelArray[4].load_off()
            elif self.vregUnderTest == "CPU":
                self.chroma.channelArray[3].load_off()
                self.chroma.channelArray[4].load_off()
            elif self.vregUnderTest == "MEMPHY"  or self.vregUnderTest == "SOC" :
                self.chroma.channelArray[3].load_off()
   
    def best_fit_slope_and_intercept(self, xs,ys):
        m = (((mean(xs)*mean(ys)) - mean(xs*ys)) /
             ((mean(xs)*mean(xs)) - mean(xs*xs)))
        
        b = mean(ys) - m*mean(xs)
        
        return m, b