# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 08:11:43 2019

@author: v-stpur
"""

from PyQt5.QtCore import QObject, QThread, pyqtSignal

import time
#from dsmcdbgFunctions import DsmcdbgFunctions
#from gainFunctions import GainFunctions
#from getVoltage import GetVoltage
#from miscellaneousFunctions import MiscellaneousFunctions
#import xlsxwriter
import timerThread
import subprocess

class BitCharacterization(object):

#    def __init__(self, vregUnderTest, DMM, adInstr, scsiCB, load, workBook, hiLow):
    def __init__(self):
        
        self.dmm                = timerThread.DMM
        self.adInstr            = timerThread.AdInstr
        self.vregUnderTest      = timerThread.VregUnderTest
        self.scsiCB             = timerThread.ScsiCB
        self.workBook           = timerThread.WorkBook
        self.Load               = timerThread.Load
        self.hiLow              = timerThread.HiLowCB
        self.dsmcdbg            = timerThread.Dsmcdbg
        self.voltMeter          = timerThread.VoltMeter
        self.misc               = timerThread.Misc

#        self.vregUnderTest      = vregUnderTest
#        self.Load               = load
#        self.dsmcdbg            = DsmcdbgFunctions(self.vregUnderTest)
#        self.voltMeter          = GetVoltage(DMM, adInstr, vregUnderTest, scsiCB)
#        self.misc               = MiscellaneousFunctions(self.vregUnderTest, self.Load)
        self.rowIndex           = 0 
#        self.workBook           = workBook
#        self.hiLow              = hiLow
        
#        self.excelFileName = "Bit Charerization_" + vregUnderTest + ".xlsx"
#        self.workBook = xlsxwriter.Workbook(self.excelFileName)
       
        self.gainHex = 0x0000
     
    def close(self):           
        self.workBook.close()
        self.voltMeter.close()

    def characterizeCoarseBits(self):           

        imonCurrent = 0
        currentSum  = 0
        rowIndex = 0
        self.ultraFineHex = 0x0000

        self.dsmcdbg.clearUltraFine(self.ultraFineHex)
        self.dsmcdbg.setOffsetRegister(0x0000)

        self.coarseBitSheet = self.workBook.add_worksheet("Coarse Bit Charerization " + self.vregUnderTest)

        rowIndex = rowIndex + 1
        self.coarseBitSheet.write(rowIndex, 0, "VIMON")
        self.coarseBitSheet.write(rowIndex, 1, "IMON")
        self.coarseBitSheet.write(rowIndex, 2, "Gain")
        self.coarseBitSheet.write(rowIndex, 3, "Offset")
        self.coarseBitSheet.write(rowIndex, 4, "CurrentStep")
        rowIndex = rowIndex + 1
        
        self.dsmcdbg.setGainRegister(self.gainHex, True)
        time.sleep(1)
        voltage = self.voltMeter.getVoltage(1)
        imonCurrent = self.misc.calculateCurrent(voltage)

        self.gainHex = 0x0800
        while self.gainHex > 0x0FC0:
            print ("Starting at Max Negative Offset")
            savedCurrent = imonCurrent
                
            self.dsmcdbg.setGainRegister(self.gainHex, True)
            time.sleep(1)
            voltage = self.voltMeter.getVoltage(1)
            imonCurrent = self.misc.calculateCurrent(voltage)
                
            self.coarseBitSheet.write(rowIndex, 0, voltage)
            self.coarseBitSheet.write(rowIndex, 1, imonCurrent)
            
            gain = self.dsmcdbg.readGainRegister(True)
            self.coarseBitSheet.write(rowIndex, 2, gain)
    
            offset = self.dsmcdbg.readOffsetRegister()
            self.coarseBitSheet.write(rowIndex, 3, offset)
    
            currentStep = imonCurrent - savedCurrent
            self.coarseBitSheet.write(rowIndex, 4, currentStep)
            print ("Current Step for One Bit is: " + str(currentStep))
            
            currentSum = currentSum + currentStep
            self.coarseBitSheet.write(rowIndex, 5, currentSum)
            print ("Current Sum is: " + str(currentSum))
            
            self.gainHex = self.gainHex - 0x0040
            rowIndex = rowIndex + 1
       
        self.gainHex = 0x0000
        while self.gainHex < 0x0FC0:
            savedCurrent = imonCurrent
                
            self.dsmcdbg.setGainRegister(self.gainHex, True)
            time.sleep(1)
            voltage = self.voltMeter.getVoltage(1)
            imonCurrent = self.misc.calculateCurrent(voltage)
                
            self.coarseBitSheet.write(rowIndex, 0, voltage)
            self.coarseBitSheet.write(rowIndex, 1, imonCurrent)
            
            gain = self.dsmcdbg.readGainRegister(True)
            self.coarseBitSheet.write(rowIndex, 2, gain)
    
            offset = self.dsmcdbg.readOffsetRegister()
            self.coarseBitSheet.write(rowIndex, 3, offset)
    
            currentStep = imonCurrent - savedCurrent
            self.coarseBitSheet.write(rowIndex, 4, currentStep)
            print ("Current Step for One Bit is: " + str(currentStep))
            
            currentSum = currentSum + currentStep
            self.coarseBitSheet.write(rowIndex, 5, currentSum)
            print ("Current Sum is: " + str(currentSum))

            self.gainHex = self.gainHex + 0x0040
            rowIndex = rowIndex + 1
            
    def characterizeFineBits(self):           

        rowIndex           = 0 
        imonCurrent = 0
        currentSum  = 0
        self.ultraFineHex = 0x0000
        self.dsmcdbg.clearUltraFine(self.ultraFineHex)
        
        self.fineBitSheet = self.workBook.add_worksheet("Fine Bit Charerization " + self.vregUnderTest)

        rowIndex = rowIndex + 1
        self.fineBitSheet.write(rowIndex, 0, "VIMON")
        self.fineBitSheet.write(rowIndex, 1, "IMON")
        self.fineBitSheet.write(rowIndex, 2, "Gain")
        self.fineBitSheet.write(rowIndex, 3, "Offset")
        self.fineBitSheet.write(rowIndex, 4, "CurrentStep")
        rowIndex = rowIndex + 1

        if self.vregUnderTest == "GFX":
            
            self.dsmcdbg.setGainRegister(0x0800, True)
            
            voltage = self.voltMeter.getVoltage(1)
            imonCurrent = self.misc.calculateCurrent(voltage)

            self.gainHex = 0x0000
            print ("Starting at Zero Fine Offset")
            while self.gainHex < 0x00FC:
                savedCurrent = imonCurrent
                    
                self.gainHex = self.gainHex + 0x0004
                rowIndex = rowIndex + 1
           
                self.dsmcdbg.setOffsetRegister(self.gainHex)
                time.sleep(1)
                voltage = self.voltMeter.getVoltage(1)
                imonCurrent = self.misc.calculateCurrent(voltage)
                    
                self.fineBitSheet.write(rowIndex, 0, voltage)
                self.fineBitSheet.write(rowIndex, 1, imonCurrent)
                
                gain = self.dsmcdbg.readGainRegister(True)
                self.fineBitSheet.write(rowIndex, 2, gain)
        
                offset = self.dsmcdbg.readOffsetRegister()
                self.fineBitSheet.write(rowIndex, 3, offset)
        
                currentStep = imonCurrent - savedCurrent
                self.fineBitSheet.write(rowIndex, 4, currentStep)
                print ("Current Step for One Bit is: " + str(currentStep))
                
                currentSum = currentSum + currentStep
                self.fineBitSheet.write(rowIndex, 5, currentSum)
                print ("Current Sum is: " + str(currentSum))

        elif self.vregUnderTest == "CPU":
            
            self.dsmcdbg.setGainRegister(0x0800, True)

            voltage = self.voltMeter.getVoltage(1)
            imonCurrent = self.misc.calculateCurrent(voltage)

            self.gainHex = 0x0000
            print ("Starting at Zero Fine Offset")
            while self.gainHex < 0x00FC:
                savedCurrent = imonCurrent
                    
                self.gainHex = self.gainHex + 0x0004
                rowIndex = rowIndex + 1
           
                self.dsmcdbg.setOffsetRegister(self.gainHex)
                time.sleep(1)
                voltage = self.voltMeter.getVoltage(1)
                imonCurrent = self.misc.calculateCurrent(voltage)
                    
                self.fineBitSheet.write(rowIndex, 0, voltage)
                self.fineBitSheet.write(rowIndex, 1, imonCurrent)
                
                gain = self.dsmcdbg.readGainRegister(True)
                self.fineBitSheet.write(rowIndex, 2, gain)
        
                offset = self.dsmcdbg.readOffsetRegister()
                self.fineBitSheet.write(rowIndex, 3, offset)
        
                currentStep = imonCurrent - savedCurrent
                self.fineBitSheet.write(rowIndex, 4, currentStep)
                print ("Current Step for One Bit is: " + str(currentStep))
                
                currentSum = currentSum + currentStep
                self.fineBitSheet.write(rowIndex, 5, currentSum)
                print ("Current Sum is: " + str(currentSum))

        elif (self.vregUnderTest == "MEMIO") or (self.vregUnderTest == "MEMPHY") or (self.vregUnderTest == "SOC"):
           
            self.dsmcdbg.setGainRegister(0x0500, True)

            self.ultraFineHex = self.dsmcdbg.readUltraFine()
            print ("Ultra Fine Register contains: " + '0x%0*X' % (4,self.ultraFineHex))
            self.dsmcdbg.setUpUltraFine(self.ultraFineHex)
            self.ultraFineHex = self.dsmcdbg.readUltraFine()
            self.dsmcdbg.clearUltraFineHighBit(self.ultraFineHex)
#            self.gainHex = 0x0780
#            while self.gainHex > 0x0000:
#                savedCurrent = imonCurrent
#                    
#                self.dsmcdbg.setOffsetRegister(self.gainHex)
#                time.sleep(1)
#                voltage = self.voltMeter.getVoltage(10)
#                imonCurrent = self.misc.calculateCurrent(voltage)
#                    
#                self.fineBitSheet.write(rowIndex, 0, voltage)
#                self.fineBitSheet.write(rowIndex, 1, imonCurrent)
#                
#                gain = self.dsmcdbg.readGainRegister()
#                self.fineBitSheet.write(rowIndex, 2, gain)
#        
#                offset = self.dsmcdbg.readOffsetRegister()
#                self.fineBitSheet.write(rowIndex, 3, offset)
#        
#                currentStep = imonCurrent - savedCurrent
#                self.fineBitSheet.write(rowIndex, 4, currentStep)
#                print ("Current Step for One Bit is: " + str(currentStep))
#                
#                currentSum = currentSum + currentStep
#                self.fineBitSheet.write(rowIndex, 5, currentSum)
#                print ("Current Sum is: " + str(currentSum))
#
#                self.gainHex = self.gainHex - 0x0040
#                rowIndex = rowIndex + 1
                
            self.gainHex = 0x0000
            self.dsmcdbg.setOffsetRegister(self.gainHex)
            voltage = self.voltMeter.getVoltage(1)
            imonCurrent = self.misc.calculateCurrent(voltage)

            self.gainHex = 0x0000
            while self.gainHex < 0x03C0:
                savedCurrent = imonCurrent
                    
                self.gainHex = self.gainHex + 0x0040
                rowIndex = rowIndex + 1
                
                self.dsmcdbg.setOffsetRegister(self.gainHex)
                time.sleep(1)
                voltage = self.voltMeter.getVoltage(1)
                imonCurrent = self.misc.calculateCurrent(voltage)
                    
                self.fineBitSheet.write(rowIndex, 0, voltage)
                self.fineBitSheet.write(rowIndex, 1, imonCurrent)
                
                gain = self.dsmcdbg.readGainRegister(True)
                self.fineBitSheet.write(rowIndex, 2, gain)
        
                offset = self.dsmcdbg.readOffsetRegister()
                self.fineBitSheet.write(rowIndex, 3, offset)
        
                currentStep = imonCurrent - savedCurrent
                self.fineBitSheet.write(rowIndex, 4, currentStep)
                print ("Current Step for One Bit is: " + str(currentStep))
                
                currentSum = currentSum + currentStep
                self.fineBitSheet.write(rowIndex, 5, currentSum)
                print ("Current Sum is: " + str(currentSum))

            self.dsmcdbg.setUltraFineHighBit(self.ultraFineHex)

            self.gainHex = 0x0000
            while self.gainHex < 0x03C0:
                savedCurrent = imonCurrent
                    
                self.gainHex = self.gainHex + 0x0040
                rowIndex = rowIndex + 1

                self.dsmcdbg.setOffsetRegister(self.gainHex)
                time.sleep(1)
                voltage = self.voltMeter.getVoltage(1)
                imonCurrent = self.misc.calculateCurrent(voltage)
                    
                self.fineBitSheet.write(rowIndex, 0, voltage)
                self.fineBitSheet.write(rowIndex, 1, imonCurrent)
                
                gain = self.dsmcdbg.readGainRegister(True)
                self.fineBitSheet.write(rowIndex, 2, gain)
        
                offset = self.dsmcdbg.readOffsetRegister()
                self.fineBitSheet.write(rowIndex, 3, offset)
        
                currentStep = imonCurrent - savedCurrent
                self.fineBitSheet.write(rowIndex, 4, currentStep)
                print ("Current Step for One Bit is: " + str(currentStep))
                
                currentSum = currentSum + currentStep
                self.fineBitSheet.write(rowIndex, 5, currentSum)
                print ("Current Sum is: " + str(currentSum))

#        elif self.vregUnderTest == "MEMPHY":
#           
#           
#            self.gainHex = 0x0780
#            while self.gainHex > 0x0000:
#                savedCurrent = imonCurrent
#                    
#                self.dsmcdbg.setOffsetRegister(self.gainHex)
#                time.sleep(1)
#                voltage = self.voltMeter.getVoltage(10)
#                imonCurrent = self.misc.calculateCurrent(voltage)
#                    
#                self.fineBitSheet.write(rowIndex, 0, voltage)
#                self.fineBitSheet.write(rowIndex, 1, imonCurrent)
#                
#                gain = self.dsmcdbg.readGainRegister()
#                self.fineBitSheet.write(rowIndex, 2, gain)
#        
#                offset = self.dsmcdbg.readOffsetRegister()
#                self.fineBitSheet.write(rowIndex, 3, offset)
#        
#                currentStep = imonCurrent - savedCurrent
#                self.fineBitSheet.write(rowIndex, 4, currentStep)
#                print ("Current Step for One Bit is: " + str(currentStep))
#                
#                currentSum = currentSum + currentStep
#                self.fineBitSheet.write(rowIndex, 5, currentSum)
#                print ("Current Sum is: " + str(currentSum))
#
#                self.gainHex = self.gainHex - 0x0040
#                rowIndex = rowIndex + 1
#                
#            self.gainHex = 0x8000
#            while self.gainHex < 0x8780:
#                savedCurrent = imonCurrent
#                    
#                self.dsmcdbg.setOffsetRegister(self.gainHex)
#                time.sleep(1)
#                voltage = self.voltMeter.getVoltage(10)
#                imonCurrent = self.misc.calculateCurrent(voltage)
#                    
#                self.fineBitSheet.write(rowIndex, 0, voltage)
#                self.fineBitSheet.write(rowIndex, 1, imonCurrent)
#                
#                gain = self.dsmcdbg.readGainRegister()
#                self.fineBitSheet.write(rowIndex, 2, gain)
#        
#                offset = self.dsmcdbg.readOffsetRegister()
#                self.fineBitSheet.write(rowIndex, 3, offset)
#        
#                currentStep = imonCurrent - savedCurrent
#                self.fineBitSheet.write(rowIndex, 4, currentStep)
#                print ("Current Step for One Bit is: " + str(currentStep))
#                
#                currentSum = currentSum + currentStep
#                self.fineBitSheet.write(rowIndex, 5, currentSum)
#                print ("Current Sum is: " + str(currentSum))
#
#                self.gainHex = self.gainHex + 0x0040
#                rowIndex = rowIndex + 1
#                
#        elif self.vregUnderTest == "SOC":
#           
#            self.gainHex = 0x0780
#            while self.gainHex > 0x0000:
#                savedCurrent = imonCurrent
#                    
#                self.dsmcdbg.setOffsetRegister(self.gainHex)
#                time.sleep(1)
#                voltage = self.voltMeter.getVoltage(10)
#                imonCurrent = self.misc.calculateCurrent(voltage)
#                    
#                self.fineBitSheet.write(rowIndex, 0, voltage)
#                self.fineBitSheet.write(rowIndex, 1, imonCurrent)
#                
#                gain = self.dsmcdbg.readGainRegister()
#                self.fineBitSheet.write(rowIndex, 2, gain)
#        
#                offset = self.dsmcdbg.readOffsetRegister()
#                self.fineBitSheet.write(rowIndex, 3, offset)
#        
#                currentStep = imonCurrent - savedCurrent
#                self.fineBitSheet.write(rowIndex, 4, currentStep)
#                print ("Current Step for One Bit is: " + str(currentStep))
#                
#                currentSum = currentSum + currentStep
#                self.fineBitSheet.write(rowIndex, 5, currentSum)
#                print ("Current Sum is: " + str(currentSum))
#
#                self.gainHex = self.gainHex - 0x0040
#                rowIndex = rowIndex + 1
#                
#            self.gainHex = 0x8000
#            while self.gainHex < 0x8780:
#                savedCurrent = imonCurrent
#                    
#                self.dsmcdbg.setOffsetRegister(self.gainHex)
#                time.sleep(1)
#                voltage = self.voltMeter.getVoltage(10)
#                imonCurrent = self.misc.calculateCurrent(voltage)
#                    
#                self.fineBitSheet.write(rowIndex, 0, voltage)
#                self.fineBitSheet.write(rowIndex, 1, imonCurrent)
#                
#                gain = self.dsmcdbg.readGainRegister()
#                self.fineBitSheet.write(rowIndex, 2, gain)
#        
#                offset = self.dsmcdbg.readOffsetRegister()
#                self.fineBitSheet.write(rowIndex, 3, offset)
#        
#                currentStep = imonCurrent - savedCurrent
#                self.fineBitSheet.write(rowIndex, 4, currentStep)
#                print ("Current Step for One Bit is: " + str(currentStep))
#                
#                currentSum = currentSum + currentStep
#                self.fineBitSheet.write(rowIndex, 5, currentSum)
#                print ("Current Sum is: " + str(currentSum))
#
#                self.gainHex = self.gainHex + 0x0040
#                rowIndex = rowIndex + 1
                
    def longTermVoltageAverage(self): 
        
        print ("Doing Long Term Voltage Average")
        
        self.rowIndex           = 0 
        self.averageSheet = self.workBook.add_worksheet("Long Term Average " + self.vregUnderTest)

#        if self.vregUnderTest == "GFX":
#            print "Setting voltage to 0.8V"
#            self.dsmcdbg.setOutputVoltage(0x0080)
#    
#        elif self.vregUnderTest == "CPU":
#            print "Setting voltage to 1.0V"
#            self.dsmcdbg.setOutputVoltage(0x00A0)
#    
#        elif self.vregUnderTest == "MEMIO":
#            print "Setting voltage to 1.35V"
#            self.dsmcdbg.setOutputVoltage(0x00D8)
#
#        elif self.vregUnderTest == "MEMPHY":
#            self.dsmcdbg.setOutputVoltage(0x0088)
#                
#        elif self.vregUnderTest == "SOC":
#            print "Setting voltage to 0.8V"
#            self.dsmcdbg.setOutputVoltage(0x0080)
                
#        self.gainHex = 0x0000
#        self.dsmcdbg.setOffsetRegister(self.gainHex)
#
        self.dsmcdbg.setUserConfigRegisters()

#        p = subprocess.Popen("dsmcdbg.exe sjm i2c wr 0x20 0x00 0x01 stop wr 0x20 0x4c 0x75F5", stdout=subprocess.PIPE, shell=True)
#        returnString = str(p.communicate())
        
        self.dsmcdbg.setOutputVoltage(0x00A0)
        time.sleep(2)
        self.misc.setChromaCurrent(58.0)
        time.sleep(2)
        self.misc.setChromaCurrent(1.0)
        time.sleep(2)
#        self.misc.setChromaCurrent(54.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(1.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(54.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(1.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(54.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(1.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(54.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(1.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(54.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(1.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(54.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(1.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(54.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(1.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(54.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(1.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(54.0)
#        time.sleep(2)
#        self.misc.setChromaCurrent(1.0)
        
        runningAverage = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #get first twenty values for average
        for loopIndex in range(0, 20):
            runningAverage[loopIndex] = self.voltMeter.getVoltage(1)

        averageCount = 0
                
        for loopIndex in range(0, 60):
            
            if loopIndex == 10:
                self.misc.loadOff()
                self.dsmcdbg.setOutputVoltage(0x0070)
                self.dsmcdbg.setOutputVoltage(0x00A0)
                self.misc.loadOn()
#                p = subprocess.Popen("dsmcdbg.exe sjm i2c wr 0x23 0x00 0x02 stop wr 0x23 0x01 0x00", stdout=subprocess.PIPE, shell=True)
#                returnString = str(p.communicate())
#                p = subprocess.Popen("dsmcdbg.exe sjm i2c wr 0x23 0x00 0x02 stop wr 0x23 0x01 0x80", stdout=subprocess.PIPE, shell=True)
#                returnString = str(p.communicate())
                print ("Setting Vout")
            elif loopIndex == 30:
#                self.misc.setChromaCurrent(98.0)
                time.sleep(2)
#                self.misc.setChromaCurrent(1.0)


                
            voltage = self.voltMeter.getVoltage(1)
            current = self.misc.calculateCurrent(voltage, self.hiLow)
            
            intelliphaseTemp = self.dsmcdbg.readIntelliTempRegister()

            runningAverage[averageCount] = voltage
                
            average = 0
            for averageIndex in range (0,20):
                average = average + runningAverage[averageIndex]
            average = average / 20 
            imonCurrent = self.misc.calculateCurrent(average, self.hiLow)
                
            print ("Averaged Current is: " + str(imonCurrent))
    
            self.averageSheet.write(self.rowIndex, 0, voltage)
            self.averageSheet.write(self.rowIndex, 1, current)
                
            self.averageSheet.write(self.rowIndex, 3, average)
            self.averageSheet.write(self.rowIndex, 4, imonCurrent)
            self.averageSheet.write(self.rowIndex, 5, intelliphaseTemp)
        
            self.rowIndex = self.rowIndex + 1
                
            averageCount = averageCount + 1
            if averageCount >= 20:
                averageCount = 0
                    
