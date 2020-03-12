# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 14:12:29 2017

@author: beschanz
"""
import chromaLib_63600 as ChromaLib
#GIT Version

class ChromaChannel():
    #index, integer represnting channel index
    #max load - integer representing maximum current capability of load.
    #loadObject - visa or TCIP resource handle
    #todo: on/off state tracking is based off state variables and doesn't track all run behavior
    def __init__(self, index, maxLoad, mode, rangeHiMedLo, loadObject):
        self.mode = mode
        self.index = index
        self.maxLoad = maxLoad
        self.loadObject = loadObject
        self.setpoint = 0
        self.rangeSetting = rangeHiMedLo
        self.channelOn = False
        self.allRun = False
        self.load1 = 0
        self.load2 = 0
        self.time1 = 0
        self.time2 = 0
        
        self.set_mode(mode)
        self.set_all_run(False)
        self.set_load(0)
        self.load_off()
        
    def set_range(self, rangeHiMedLo):
        ChromaLib.setRangeHiMedLo(self.loadObject, self.index, rangeHiMedLo)
        
    def set_mode(self, mode):
        ChromaLib.setMode(self.loadObject, self.index, mode, self.rangeSetting)
        
    def set_all_run(self, onOffBool):
        ChromaLib.setAllRun(self.loadObject, self.index, onOffBool)
        self.allRun = onOffBool
        
    def set_dynamic_load(self, load1, load2, time1, time2):
        ChromaLib.setDynamicLoadPoint(self.loadObject, self.index, load1, load2, time1, time2)
        self.load1 = load1
        self.load2 = load2
        self.time1 = time1
        self.time2 = time2
    
    def load_on(self):
        ChromaLib.setLoadOn(self.loadObject, self.index)
        self.channelOn = True
        
    def load_off(self):
        ChromaLib.setLoadOff(self.loadObject, self.index)
        self.channelOn = False
        
    def set_load(self, loadAmps):
        ChromaLib.setLoad(self.loadObject, self.index, loadAmps)
        self.setpoint = loadAmps
        
    def get_max_load(self):
        return self.maxLoad
    
    def get_index(self):
        return self.index
    
    def get_measured_voltage(self):
        return ChromaLib.fetchVoltage(self.loadObject, self.index)
        
    def get_measured_current(self):
        return ChromaLib.fetchCurrent(self.loadObject, self.index) 
        
    def channel_info(self):
        infoStr = "Index: " + str(self.index)
        infoStr = infoStr + (", Max: " + str(self.maxLoad))
        infoStr = infoStr + (", Visa: " + str(self.loadObject))
        infoStr = infoStr + (", Setpoint: " + str(self.setpoint))
        infoStr = infoStr + (", rangeSetting: " + str(self.rangeSetting))
        infoStr = infoStr + (", On?: " + str(self.channelOn))
        infoStr = infoStr + (", AllRun?: " + str(self.allRun))
        return infoStr
        
        
class ChromaMainframe():
    def __init__(self, loadObject):
        self.channelArray = []
        self.loadObject = loadObject
        self.totalMaxLoad = 0
        self.loadOn = False
        
    def add_channel(self, index, maxLoad, mode, rangeHiMedLo):
        self.channelArray.append(ChromaChannel(index, maxLoad, mode, rangeHiMedLo, self.loadObject))
        self.totalMaxLoad = self.totalMaxLoad + maxLoad
    
    def remove_channel(self, index):
        for channel in self.channelArray:
            if channel.get_index() is index:
                self.totalMaxLoad = self.totalMaxLoad - channel.get_max_load()
                self.channelArray.remove(channel)
                
    def remove_all_channels(self): #redundant, you could also just create a new chromaMainFrame and reassign
        self.channelArray = []
        self.totalMaxLoad = 0
                
    def set_load_distributed(self, load):
        if load > self.totalMaxLoad:
            raise ValueError('specified load exceeds max possible load')
            return
        remainingLoad = load
        for channel in self.channelArray:
            if channel.get_max_load() < remainingLoad:
                #set channel to max load and go to the next channel
                channel.set_load(channel.get_max_load())
                remainingLoad = remainingLoad - channel.get_max_load()
            else:
                #remaining load to distribute is less than channel maximum. set load, then break
                channel.set_load(remainingLoad)
                remainingLoad = 0
                break
    
    #set load current for individual channels
    #index is either an integer or array of integers representing which channels to modify
    #load is an intger or array of integers with the load for the respective channel
    #for example: set_load_single_channels([1,2], [2,3]) would set ch1 to 2A, and ch2 to 3A
    #             set_laod_single_channels(1,2) would set ch1 to 2A
    def set_load_single_channels(self, index, load):
        #convert variable arguments to lists
        if not hasattr(index, "__iter__"):
            index = [index]
        if not hasattr(load, "__iter__"):
            load = [load]
            
        #check for equal size inputs
        if len(index) is not len(load):
            raise ValueError('index and load must be same dimensions')
            return
        
        #iterate over specified channel indices. using iterator so I have count to index load argument
        for i in range(0, len(index)):
            #go through our channel array until we find the correct channel.. probably a better way to do this..
            for channel in self.channelArray:
                if channel.get_index() is index[i]:
                    channel.set_load(load[i])
                    break 
        #todo: haven't tried this function, hopefully it works :)
        
    def all_channels_on(self):  #todo: get allRun working so loads come on simultaneously
        for channel in self.channelArray:
            channel.set_all_run(True)
            channel.load_on()
        #self.channelArray[0].load_on() #if allrun worked, this would turn on all set channels
        self.loadOn = True
    
    def all_channels_off(self):
        for channel in self.channelArray:
            channel.load_off()
            channel.set_all_run(False)
        self.loadOn = False
        
    def set_dynamic_load(self, index, l1, l2, t1, t2):
         for channel in self.channelArray:
            if channel.get_index() == int(index):
                channel.set_dynamic_load(l1,l2,t1,t2)
                
                
            
    #channelList is a list of indicies representing chroma channels, i.e.[1,2,3]
    #use this function if you only want to turn on specific channels, instead of all instantiated channels
    def select_channels_on(self, channelList):
        for channel in self.channelArray:
            if channel.get_index() in channelList:
                channel.set_all_run(True)
            else:
                channel.set_all_run(False)
        for channel in self.channelArray:
            if channel.get_index() in channelList:
                channel.load_on(True)
                #break if allRun starts working, could break here
        self.loadOn = True
    
    #idk why anybody would use this instead of all_channels_off, but its here now
    def select_channels_off(self, channelList):
        for channel in self.channelArray:
            if channel.get_index() in channelList:
                channel.load_off()
                channel.set_all_run(False)
        self.loadOn = False
    
    def get_measured_total_current(self):
        totalCurrent = 0.0
        for channel in self.channelArray:
            totalCurrent = totalCurrent + float((channel.get_measured_current()))
        return totalCurrent
    
    def get_measured_channel_current(self, index):
        for channel in self.channelArray:
            if channel.get_index() is index:
                current = float(channel.get_measured_current())
                return current
        raise ValueError('Given index not in chroma configuration')
    
    def get_measured_channel_voltage(self, index):
        for channel in self.channelArray:
            if channel.get_index() is index:
                voltage = float(channel.get_measured_voltage())
                return voltage
        raise ValueError('Given index not in chroma configuration')
        
    def load_info(self):
        infoStr = "Total Capacity:" + str(self.totalMaxLoad)
        for channel in self.channelArray:
            infoStr = infoStr + "\n" + channel.channel_info()
        return infoStr
            
            
            