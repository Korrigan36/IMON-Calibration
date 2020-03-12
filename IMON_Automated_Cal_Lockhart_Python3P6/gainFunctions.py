# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 13:39:37 2019

@author: v-stpur
"""
import time
import timerThread

version_Info = "Python PyQt5 Lockhart IMON Automated Calibration V1.1"

class GainFunctions(object):

    def __init__(self):
        
        #Create local versions of globals so code below doesn't change
        self.vregUnderTest      = timerThread.VregUnderTest
        self.dmm                = timerThread.DMM
        self.adInstr            = timerThread.AdInstr
        self.runNotes           = timerThread.RunNotes
        self.Load               = timerThread.Load
        self.configID           = timerThread.ConfigID
        self.pcbaSN             = timerThread.PcbaSN
        self.productSN          = timerThread.ProductSN
        self.logFilePointer     = timerThread.LogFilePointer
#        self.scsiCB             = timerThread.ScsiCB
        self.offsetCount        = 0
        
        self.dsmcdbg            = timerThread.Dsmcdbg
        self.voltMeter          = timerThread.VoltMeter
        self.misc               = timerThread.Misc
        self.rowIndex           = 0 
        self.workBook           = timerThread.WorkBook
        self.summarySheet       = timerThread.SummarySheet
        self.plotSheet          = timerThread.PlotSheet

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
        self.gfxTdc         = float(timerThread.GfxTdc)
        self.cpuTdc         = float(timerThread.CpuTdc)
        self.memphyTdc      = float(timerThread.MemphyTdc)
        self.socTdc         = float(timerThread.SocTdc)
        self.gfxMinload     = float(timerThread.GfxMinload)
        self.cpuMinload     = float(timerThread.CpuMinload)
        self.memphyMinload  = float(timerThread.MemphyMinload)
        self.socMinload     = float(timerThread.SocMinload)
        self.lowCurrentGFX  = timerThread.LowCurrentGFX
        self.lockHart       = timerThread.LockHartCB

        tempString = self.runNotes
        tempString = tempString.replace(" ", "_")
        tempString = tempString.replace(":", "_")
        tempString = tempString.replace("-", "_")
        
        self.headerCellFormat = self.workBook.add_format()
        self.headerCellFormat.set_font_size(16)
        self.headerCellFormat.set_bold()
        
    def testInterface(self):
        return self.dsmcdbg.testDsmcdbgInterface()
        
    def gainLoopMPS(self, gainHex):

        self.logFilePointer.write("Doing MPS Gain Method for " + self.vregUnderTest + "\n\n")
        print ("Doing MPS Gain Method")
        
        self.gainHex = gainHex
        if self.vregUnderTest == "GFX":
            minPercent = 0.007
            GIMON = self.gfxGain #/16x
            Gcs   = self.gfxKcs #uA/A
            RIMON = self.gfxRimon #kOhms
            TDC = self.gfxTdc
        elif self.vregUnderTest == "CPU":
            minPercent = 0.005
            RIMON = self.cpuRimon #kOhms
            GIMON = self.cpuGain #/8x
            Gcs   = self.cpuKcs #uA/A
            TDC = self.cpuTdc
        elif self.vregUnderTest == "SOC":
            minPercent = 0.005
            RIMON = self.socRimon #kOhms
            GIMON = self.socGain #/16x
            Gcs   = self.socKcs #uA/A
            TDC = self.socTdc
        elif self.vregUnderTest == "MEMPHY":
            minPercent = 0.009
            RIMON = self.memphyRimon #kOhms
            GIMON = self.memphyGain #/16x
            Gcs   = self.memphyKcs #uA/A
            TDC = self.memphyTdc
        
#        ideal_VIMON_gain = Gcs / 16.0 * GIMON * RIMON
        ideal_VIMON_gain = Gcs / GIMON * RIMON
        print ("Ideal VIMON Gain: " + str(ideal_VIMON_gain))
#        VIMON_0A = 10.0 * ideal_VIMON_gain
#        print "Ideal VIMON at 0A: " + str(VIMON_0A)

        loopIndex = 0
        continueLoop = True
        firstTime = True
        countSuccess = 0
        while continueLoop:
            
            self.misc.setChromaCurrent(0.0)
            self.misc.loadOn()
            time.sleep(2)

            self.logFilePointer.write("Dsmcdbg: Setting gain to: " + '0x%0*X' % (4,self.gainHex) + "\n")
            self.dsmcdbg.setGainRegister(self.gainHex)
            self.logFilePointer.write("Dsmcdbg: read gain register\n")
            self.dsmcdbg.readGainRegister()

            vImon = self.voltMeter.getVoltage(1)
    
            zeroLoadIMON = vImon
            #Convert to mV
            zeroLoadIMON = zeroLoadIMON * 1000
            print ("Zero Load IMON: " + str(zeroLoadIMON))

            #Set Load to TDC
            print ("Setting chroma to TDC: " + str(TDC))
            self.misc.setChromaCurrent(TDC)
            time.sleep(2)

            vImon = self.voltMeter.getVoltage(1)
            
            readBackLoad = self.misc.readBackLoad()
            self.misc.loadOff()
    
            #Convert to mV
            tdcIMON = vImon * 1000
            print ("TDC IMON: " + str(tdcIMON))
            #Run hardcoded for now will use slider later
            slope = (tdcIMON - zeroLoadIMON)/(readBackLoad)
            self.logFilePointer.write("Gain is: " + str(slope) + "\n")
            print ("Gain is: " + str(slope))
            
            
            if slope > ideal_VIMON_gain:
                gainError = slope / ideal_VIMON_gain - 1
                print ("Gain Error is greater than ideal: " + str(gainError))
                gainGreater = True
            else:
                gainError = 1 - slope / ideal_VIMON_gain
                print ("Gain Error is less than ideal: " + str(gainError))
                gainGreater = False
            self.logFilePointer.write("Gain Error is: " + str(gainError) + "\n")
            
            if abs(gainError) < minPercent:
                #Go again a few times just to be sure
                self.logFilePointer.write("No further gain correction needed\n")
                print ("No further gain correction needed")
                countSuccess = countSuccess + 1
                if countSuccess > 3:
                    continueLoop = False
            elif gainGreater and firstTime:
                #Or in the sign bit
                print ("got to here")
                self.gainHex = self.gainHex | 0b0000000000100000
                self.gainHex = self.gainHex & 0b1111111111100000
                firstTime = False
            elif abs(gainError) > minPercent: 
                self.gainHex = self.gainHex + 1
                   
            loopIndex = loopIndex + 1
            
            #Heating causes drift so lets cool down a while
            if self.vregUnderTest == "GFX":
                time.sleep(10)
            elif self.vregUnderTest == "CPU":
                time.sleep(5)

        return self.gainHex

    def offsetLoopMPS(self, gainHex):
        
        self.offsetCount += 1
        
        self.logFilePointer.write("Doing MPS Offset Loop for " + self.vregUnderTest + "\n\n")
        print ("Doing MPS Offset Loop")
        self.gainHex = gainHex
        self.fineHex = 0x0000
        self.ultraFineHex = 0x0000
        target = 0
        minLoad = 0

        if self.vregUnderTest == "GFX":
            minError = 0.36
            target = 10.0
            minLoad = self.gfxMinload
            
        elif self.vregUnderTest == "CPU":
            minError = 0.29
            target = 10.0
            minLoad = self.cpuMinload
            
        elif self.vregUnderTest == "SOC":
            minError = 0.23
            target = 5.0
            minLoad = self.socMinload
            
            self.ultraFineHex = self.dsmcdbg.readUltraFine()
            self.ultraFineHex = self.dsmcdbg.readUltraFine()
            print ("Ultra Fine Register contains: " + self.ultraFineHex)

        elif self.vregUnderTest == "MEMPHY":
            minError = 0.21
            target = 5.0
            minLoad = self.memphyMinload
           
            self.ultraFineHex = self.dsmcdbg.readUltraFine()
            self.ultraFineHex = self.dsmcdbg.readUltraFine()
            print ("Ultra Fine Register contains: " + self.ultraFineHex)
        

        self.misc.setChromaCurrent(minLoad)
        self.misc.loadOn()
        time.sleep(2)
        
        readBackLoad = self.misc.readBackLoad()

        offsetLoop = True
        countSuccess = 0
        while offsetLoop:
            
            vImon = self.voltMeter.getVoltage(1)
            print ("VIMON is: " + str(vImon))
            imon = self.misc.calculateCurrent(vImon)
            print ("IMON is: " + str(imon))
            readBackLoad = self.misc.readBackLoad()
            offset_Error = (imon - (target + readBackLoad))
            print ("Offset Error Method 3: " + str(offset_Error))
            self.logFilePointer.write("Offset Error at MIN: " + str(offset_Error) + "\n")
            
            #No need for sign bit because we always start with large offset
            if offset_Error > minError: 
                countSuccess = 0
                self.logFilePointer.write("Adjust Offset Down 1 LSB at a time\n")
                print ("Adjust Offset Down 1 LSB at a time")
                        
                #Set Offset to one less than last run
                self.gainHex = self.gainHex - 0x0040
                self.dsmcdbg.setGainRegister(self.gainHex)
                self.logFilePointer.write("Setting gain to: " + '0x%0*X' % (4,self.gainHex) + "\n")
                
            elif offset_Error < -minError:
                countSuccess = 0
                self.logFilePointer.write("Adjust Offset Up 1 LSB at a time\n")
                print ("Adjust Offset Up 1 LSB at a time")
                
                #Set Offset to one more than last run
                self.gainHex = self.gainHex + 0x0040
                self.dsmcdbg.setGainRegister(self.gainHex)
                self.logFilePointer.write("Setting gain to: " + '0x%0*X' % (4,self.gainHex) + "\n")
                
            else:
                self.logFilePointer.write("No Coarse Offset Adjustment Needed\n")
                print ("No Coarse Offset Adjustment Needed")
                countSuccess = countSuccess + 1
                time.sleep(3)
                if countSuccess > 4:
                    offsetLoop = False
            
            offset = self.dsmcdbg.readGainRegister()
            self.logFilePointer.write("Gain setting is now: " + str(offset) + "\n")
            print ("Gain setting is now: " + str(offset))
            
        self.misc.setChromaCurrent(minLoad)
        self.misc.loadOn()
        time.sleep(2)

        vImon = self.voltMeter.getVoltage(1)
        print ("VIMON is: " + str(vImon))
        imon = self.misc.calculateCurrent(vImon)
        print ("IMON is: " + str(imon))
        readBackLoad = self.misc.readBackLoad()
        offset_Error = (imon - (target + readBackLoad))
        print ("Offset Error Method 3: " + str(offset_Error))
                    
        self.summarySheet.write(timerThread.TweakCell, offset_Error)
                
        print ("")
        self.logFilePointer.write("Offset Error at Min Load: " + str(offset_Error) + "\n")
        print ("Offset Error at Min Load: " + str(offset_Error))
        print ("")
            
        offset = self.dsmcdbg.readOffsetRegister()
        self.logFilePointer.write("Fine offset setting is now: " + str(offset) + "\n")
        print ("Fine offset setting is now: " + str(offset))
        print ("")
            
        self.misc.loadOff()

        return self.gainHex, offset_Error
    
    def imonCheck(self, sheetCount):
        
        print ("Doing IMON Check")
        self.logFilePointer.write("Doing Load Sweep for " + self.vregUnderTest + "\n\n")
        self.rowIndex = 0
#        self.summaryRowIndex = 0
        voutHex = 0x00A0
        self.dsmcdbg.enablePMBusMode()
        
        if self.vregUnderTest == "GFX" and ((not self.lowCurrentGFX) or self.lockHart):
            dmmSheet = self.workBook.add_worksheet(str(sheetCount) + "IMON " + self.vregUnderTest + " " + "High")
            dmmSheetName =  "'" + str(sheetCount) + "IMON " + self.vregUnderTest + " " + "High'"
            plotName = "GFX High Range Error Delta"
            percentName = "GFX High Range Percent Error"
            
            if sheetCount == 1:
                timerThread.ImonChartGFXHi = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                timerThread.ImonChartGFXHi.set_x_axis({'name': 'Chroma Load (Amps)'})
                timerThread.ImonChartGFXHi.set_y_axis({'name': 'Error (Amps)'})
                timerThread.ImonChartGFXHi.set_title({'name': plotName})  
                timerThread.ImonChartGFXHi.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
                
                timerThread.PercentChartGFXHi = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                timerThread.PercentChartGFXHi.set_x_axis({'name': 'Chroma Load (Amps)'})
                timerThread.PercentChartGFXHi.set_y_axis({'name': 'Percent Error'})
                timerThread.PercentChartGFXHi.set_title({'name': percentName})  
                timerThread.PercentChartGFXHi.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
                
        elif self.vregUnderTest == "GFX" and self.lowCurrentGFX and (not self.lockHart):
            dmmSheet = self.workBook.add_worksheet(str(sheetCount) + "IMON " + self.vregUnderTest + " " + "Low")
            dmmSheetName =  "'" + str(sheetCount) + "IMON " + self.vregUnderTest + " " + "Low'"
            plotName = "GFX Low Range Error Delta"
            percentName = "GFX Low Range Percent Error"
            
            if sheetCount == 1:
                timerThread.ImonChartGFXLow = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                timerThread.ImonChartGFXLow.set_x_axis({'name': 'Chroma Load (Amps)'})
                timerThread.ImonChartGFXLow.set_y_axis({'name': 'Error (Amps)'})
                timerThread.ImonChartGFXLow.set_title({'name': plotName})  
                timerThread.ImonChartGFXLow.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
                
                timerThread.PercentChartGFXLow = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                timerThread.PercentChartGFXLow.set_x_axis({'name': 'Chroma Load (Amps)'})
                timerThread.PercentChartGFXLow.set_y_axis({'name': 'Percent Error'})
                timerThread.PercentChartGFXLow.set_title({'name': percentName})  
                timerThread.PercentChartGFXLow.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
                
        elif self.vregUnderTest == "CPU":
            dmmSheet = self.workBook.add_worksheet(str(sheetCount) + "IMON " + self.vregUnderTest)
            dmmSheetName =  "'" + str(sheetCount) + "IMON " + self.vregUnderTest + "'"
            plotName = self.vregUnderTest + " Error Delta"
            percentName = self.vregUnderTest + " Percent Error"
            
            if sheetCount == 1:
                timerThread.ImonChartCPU = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                timerThread.ImonChartCPU.set_x_axis({'name': 'Chroma Load (Amps)'})
                timerThread.ImonChartCPU.set_y_axis({'name': 'Error (Amps)'})
                timerThread.ImonChartCPU.set_title({'name': plotName})  
                timerThread.ImonChartCPU.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
                
                timerThread.PercentChartCPU = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                timerThread.PercentChartCPU.set_x_axis({'name': 'Chroma Load (Amps)'})
                timerThread.PercentChartCPU.set_y_axis({'name': 'Percent Error'})
                timerThread.PercentChartCPU.set_title({'name': percentName})  
                timerThread.PercentChartCPU.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
                
        elif self.vregUnderTest == "MEMPHY":
            dmmSheet = self.workBook.add_worksheet(str(sheetCount) + "IMON " + self.vregUnderTest)
            dmmSheetName =  "'" + str(sheetCount) + "IMON " + self.vregUnderTest + "'"
            plotName = self.vregUnderTest + " Error Delta"
            percentName = self.vregUnderTest + " Percent Error"
            
            if sheetCount == 1:
                timerThread.ImonChartMEMPHY = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                timerThread.ImonChartMEMPHY.set_x_axis({'name': 'Chroma Load (Amps)'})
                timerThread.ImonChartMEMPHY.set_y_axis({'name': 'Error (Amps)'})
                timerThread.ImonChartMEMPHY.set_title({'name': plotName})  
                timerThread.ImonChartMEMPHY.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
                
                timerThread.PercentChartMEMPHY = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                timerThread.PercentChartMEMPHY.set_x_axis({'name': 'Chroma Load (Amps)'})
                timerThread.PercentChartMEMPHY.set_y_axis({'name': 'Percent Error'})
                timerThread.PercentChartMEMPHY.set_title({'name': percentName})  
                timerThread.PercentChartMEMPHY.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
                
        elif self.vregUnderTest == "SOC":
            dmmSheet = self.workBook.add_worksheet(str(sheetCount) + "IMON " + self.vregUnderTest)
            dmmSheetName =  "'" + str(sheetCount) + "IMON " + self.vregUnderTest + "'"
            plotName = self.vregUnderTest + " Error Delta"
            percentName = self.vregUnderTest + " Percent Error"
            
            if sheetCount == 1:
                timerThread.ImonChartSOC = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                timerThread.ImonChartSOC.set_x_axis({'name': 'Chroma Load (Amps)'})
                timerThread.ImonChartSOC.set_y_axis({'name': 'Error (Amps)'})
                timerThread.ImonChartSOC.set_title({'name': plotName})  
                timerThread.ImonChartSOC.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
                
                timerThread.PercentChartSOC = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
                timerThread.PercentChartSOC.set_x_axis({'name': 'Chroma Load (Amps)'})
                timerThread.PercentChartSOC.set_y_axis({'name': 'Percent Error'})
                timerThread.PercentChartSOC.set_title({'name': percentName})  
                timerThread.PercentChartSOC.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
                
        dmmSheet.set_column(8, 8, 33)

            
        headerCellFormat = self.workBook.add_format()
        headerCellFormat.set_font_size(18)
        headerCellFormat.set_bold()
        headerCellFormat.set_bg_color('#2c749e')

#        if sheetCount == 1:
#            self.imonChart = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
#            self.imonChart.set_x_axis({'name': 'Chroma Load (Amps)'})
#            self.imonChart.set_y_axis({'name': 'Error (Amps)'})
#            self.imonChart.set_title({'name': plotName})  
#            self.imonChart.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
#            
#            self.percentChart = self.workBook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
#            self.percentChart.set_x_axis({'name': 'Chroma Load (Amps)'})
#            self.percentChart.set_y_axis({'name': 'Percent Error'})
#            self.percentChart.set_title({'name': percentName})  
#            self.percentChart.set_size({'x_scale': 1.5, 'y_scale': 1.5}) 
#        
        for i in range(0,40):
            self.plotSheet.write(0, i, "", headerCellFormat)
            self.plotSheet.write(46, i, "", headerCellFormat)
            self.plotSheet.write(92, i, "", headerCellFormat)
            self.plotSheet.write(138, i, "", headerCellFormat)
            self.plotSheet.write(185, i, "", headerCellFormat)
        self.plotSheet.write(0, 2, "GFX Plots High Current Calibration", headerCellFormat)
        self.plotSheet.write(46, 2, "GFX Plots Low Current Calibration", headerCellFormat)
        self.plotSheet.write(92, 2, "CPU Plots", headerCellFormat)
        self.plotSheet.write(138, 2, "MEMPHY Plots", headerCellFormat)
        self.plotSheet.write(185, 2, "SOC Plots", headerCellFormat)

        
        self.write_Measurement_Header(dmmSheet)
        self.rowIndex = self.rowIndex + 1

        chromaLoad = 0
        
        self.misc.setChromaCurrent(0.0)
        self.misc.loadOn()
        time.sleep(2)
        
        self.dsmcdbg.setOutputVoltage(voutHex)
        
        for voltIndex in range(0,2):
                        
            if voltIndex == 1:
                self.dsmcdbg.setOutputVoltage(0x0070)
                self.misc.setChromaCurrent(0.0)
                time.sleep(2)

            loopIndex = 0
            loopCount = 25
            for loopIndex in range(0, loopCount):
                
                self.misc.loadOn()
                time.sleep(2)

                if loopIndex <= 5:
                    imonVoltage = self.voltMeter.getVoltage(4)
                elif (loopIndex > 5) and (loopIndex > 10):
                    imonVoltage = self.voltMeter.getVoltage(2)
                else:
                    imonVoltage = self.voltMeter.getVoltage(1)
    
                readBackLoad = self.misc.readBackLoad()
                    
                gain = self.dsmcdbg.readGainRegister()
                intelliphaseTemp = self.dsmcdbg.readIntelliTempRegister()
                
                if (self.vregUnderTest) == "GFX" or (self.vregUnderTest == "CPU"):
                    print ("no ultra-fine")
                else:
                    ultraFine = self.dsmcdbg.readUltraFine()
                
                fineOffset = self.dsmcdbg.readOffsetRegister()
            
                vout = self.voltMeter.getVout(1)
                dmmSheet.write(self.rowIndex, 0, vout)
                dmmSheet.write(self.rowIndex, 1, float(readBackLoad))
                dmmSheet.write(self.rowIndex, 2, imonVoltage)
                dmmSheet.write(self.rowIndex, 3, "=C" + str(self.rowIndex+1) + " * Summary!" + timerThread.ScalingFactorCell)
                            
                dmmSheet.write(self.rowIndex, 4, "=D" + str(self.rowIndex+1) + " - " + "B" + str(self.rowIndex+1))
                dmmSheet.write(self.rowIndex, 5, "=E" + str(self.rowIndex+1) +  " - Summary!" + timerThread.NoLoadOffsetCell)
                dmmSheet.write(self.rowIndex, 6, "=F" + str(self.rowIndex+1) +  "/" + "B" + str(self.rowIndex+1) +  " * 100")
    
                #Tweaked Correction
                if voltIndex == 0: 
                    dmmSheet.write(self.rowIndex, 7, "=F" + str(self.rowIndex+1) + " - Summary!" + timerThread.TweakCell)
                else:
                    dmmSheet.write(self.rowIndex, 7, "=F" + str(self.rowIndex+1) + " - Summary!" + timerThread.TweakCell + "- " + "Summary!" + timerThread.OffsetCell + "- "  + "Summary!" + timerThread.CorrectionCell  + "* A" + str(self.rowIndex+1))
                dmmSheet.write(self.rowIndex, 8, "=H" + str(self.rowIndex+1) + "/ B" + str(self.rowIndex+1) + "* 100")

                dmmSheet.write(self.rowIndex, 9, gain)
                dmmSheet.write(self.rowIndex, 10, fineOffset)
                if (self.vregUnderTest) == "GFX" or (self.vregUnderTest == "CPU"):
                    dmmSheet.write(self.rowIndex, 11, "n/a")
                else:
                    dmmSheet.write(self.rowIndex, 11, ultraFine)
                dmmSheet.write(self.rowIndex, 12, intelliphaseTemp)
#                dmmSheet.write(self.rowIndex, 16, "TBD")
                         
                self.rowIndex = self.rowIndex + 1
                
                if self.vregUnderTest == "GFX":
                    if loopIndex < 10:
                        chromaLoad = chromaLoad + 1.0
                    else:
                        chromaLoad = chromaLoad + (self.gfxTdc - 10) / (loopCount - 10)
                        if loopIndex > 22:
                            self.misc.loadOff()
                            time.sleep(5)
                elif self.vregUnderTest == "CPU":
                    if loopIndex < 10:
                        chromaLoad = chromaLoad + 0.5
                    else:
                        chromaLoad = chromaLoad + (self.cpuTdc - 5) / (loopCount - 10)
#                        chromaLoad = chromaLoad + 4.3
                elif self.vregUnderTest == "MEMPHY":
                    chromaLoad = chromaLoad + self.memphyTdc / loopCount
                elif self.vregUnderTest == "SOC":
                    if loopIndex < 10:
                        chromaLoad = chromaLoad + 0.5
                    else:
                        chromaLoad = chromaLoad + (self.socTdc - 5) / (loopCount - 10)
                    
                print ("setting current to: " + str(chromaLoad))
                self.misc.setChromaCurrent(chromaLoad)
    
                print ("loopIndex is: " + str(loopIndex))
                print ("chroma load is: " + str(chromaLoad))
                
            if self.vregUnderTest == "GFX":
                if (not self.lowCurrentGFX) or self.lockHart:
                    if voltIndex == 0: 
                        timerThread.ImonChartGFXHi.add_series({'categories': '=' + dmmSheetName + '!$B$3:$B$26','values':'=' + dmmSheetName + '!$H$3:$H$26', 'name': self.vregUnderTest + " 1V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                        timerThread.PercentChartGFXHi.add_series({'categories': '=' + dmmSheetName + '!$B$3:$B$26','values':'=' + dmmSheetName + '!$I$3:$I$26', 'name': self.vregUnderTest + " 1V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                    else:
                        timerThread.ImonChartGFXHi.add_series({'categories': '=' + dmmSheetName + '!$B$30:$B$53','values':'=' + dmmSheetName + '!$H$30:$H$53', 'name': self.vregUnderTest + " 0.7V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                        timerThread.PercentChartGFXHi.add_series({'categories': '=' + dmmSheetName + '!$B$30:$B$53','values':'=' + dmmSheetName + '!$I$30:$I$53', 'name': self.vregUnderTest + " 0.7V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                else:
                    if voltIndex == 0: 
                        timerThread.ImonChartGFXLow.add_series({'categories': '=' + dmmSheetName + '!$B$3:$B$26','values':'=' + dmmSheetName + '!$H$3:$H$26', 'name': self.vregUnderTest + " 1V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                        timerThread.PercentChartGFXLow.add_series({'categories': '=' + dmmSheetName + '!$B$3:$B$26','values':'=' + dmmSheetName + '!$I$3:$I$26', 'name': self.vregUnderTest + " 1V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                    else:
                        timerThread.ImonChartGFXLow.add_series({'categories': '=' + dmmSheetName + '!$B$30:$B$53','values':'=' + dmmSheetName + '!$H$30:$H$53', 'name': self.vregUnderTest + " 0.7V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                        timerThread.PercentChartGFXLow.add_series({'categories': '=' + dmmSheetName + '!$B$30:$B$53','values':'=' + dmmSheetName + '!$I$30:$I$53', 'name': self.vregUnderTest + " 0.7V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
            elif self.vregUnderTest == "CPU":
                if voltIndex == 0: 
                    timerThread.ImonChartCPU.add_series({'categories': '=' + dmmSheetName + '!$B$3:$B$26','values':'=' + dmmSheetName + '!$H$3:$H$26', 'name': self.vregUnderTest + " 1V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                    timerThread.PercentChartCPU.add_series({'categories': '=' + dmmSheetName + '!$B$3:$B$26','values':'=' + dmmSheetName + '!$I$3:$I$26', 'name': self.vregUnderTest + " 1V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                else:
                    timerThread.ImonChartCPU.add_series({'categories': '=' + dmmSheetName + '!$B$30:$B$53','values':'=' + dmmSheetName + '!$H$30:$H$53', 'name': self.vregUnderTest + " 0.7V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                    timerThread.PercentChartCPU.add_series({'categories': '=' + dmmSheetName + '!$B$30:$B$53','values':'=' + dmmSheetName + '!$I$30:$I$53', 'name': self.vregUnderTest + " 0.7V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
            elif self.vregUnderTest == "MEMPHY":
                if voltIndex == 0: 
                    timerThread.ImonChartMEMPHY.add_series({'categories': '=' + dmmSheetName + '!$B$3:$B$26','values':'=' + dmmSheetName + '!$H$3:$H$26', 'name': self.vregUnderTest + " 1V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                    timerThread.PercentChartMEMPHY.add_series({'categories': '=' + dmmSheetName + '!$B$3:$B$26','values':'=' + dmmSheetName + '!$I$3:$I$26', 'name': self.vregUnderTest + " 1V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                else:
                    timerThread.ImonChartMEMPHY.add_series({'categories': '=' + dmmSheetName + '!$B$30:$B$53','values':'=' + dmmSheetName + '!$H$30:$H$53', 'name': self.vregUnderTest + " 0.7V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                    timerThread.PercentChartMEMPHY.add_series({'categories': '=' + dmmSheetName + '!$B$30:$B$53','values':'=' + dmmSheetName + '!$I$30:$I$53', 'name': self.vregUnderTest + " 0.7V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
            elif self.vregUnderTest == "SOC":
                if voltIndex == 0: 
                    timerThread.ImonChartSOC.add_series({'categories': '=' + dmmSheetName + '!$B$3:$B$26','values':'=' + dmmSheetName + '!$H$3:$H$26', 'name': self.vregUnderTest + " 1V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                    timerThread.PercentChartSOC.add_series({'categories': '=' + dmmSheetName + '!$B$3:$B$26','values':'=' + dmmSheetName + '!$I$3:$I$26', 'name': self.vregUnderTest + " 1V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                else:
                    timerThread.ImonChartSOC.add_series({'categories': '=' + dmmSheetName + '!$B$30:$B$53','values':'=' + dmmSheetName + '!$H$30:$H$53', 'name': self.vregUnderTest + " 0.7V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})
                    timerThread.PercentChartSOC.add_series({'categories': '=' + dmmSheetName + '!$B$30:$B$53','values':'=' + dmmSheetName + '!$I$30:$I$53', 'name': self.vregUnderTest + " 0.7V" + "Pass " + str(sheetCount), 'marker': {'type': 'diamond', 'size': 5}})

            self.misc.loadOff()
            if voltIndex == 0:
                time.sleep(60)
            self.rowIndex = self.rowIndex + 2
            chromaLoad = 0
            
        self.misc.loadOff()
        self.dsmcdbg.setOutputVoltage(0x00A0)

    def defaultWorkBookConfig(self, dmmSheet):

        dmmSheet.write('A1', self.excelFileName, self.headerCellFormat)
        dmmSheet.write('A2', version_Info, self.headerCellFormat) 
        dmmSheet.write('A3', "Config ID", self.headerCellFormat)
        dmmSheet.write('B3', self.configID)
        dmmSheet.write('A4', "PCBA S.N.", self.headerCellFormat)
        dmmSheet.write('B4', self.pcbaSN)
        dmmSheet.write('A5', "Product S.N.", self.headerCellFormat)
        dmmSheet.write('B5', self.productSN)
        dmmSheet.write('A8', "Date:", self.headerCellFormat)
        dmmSheet.write('A9', "Notes:", self.headerCellFormat)
        dmmSheet.write('B9', self.runNotes)
        dmmSheet.write('A10', "RLL", self.headerCellFormat)
        
        self.rowIndex = 11

    def write_Measurement_Header(self, dmmSheet):
        
        headerArray1 = ["Vout ","Chroma (Amps)", "VIMON (Volts)","IMON (Amps)",  "IMON - Chroma (Amps) ", "Error (Amps)", "% Error",  "No Load Adjusted Error (Amps)", "No Load Adjusted % Error", "Gain", "Fine Offset", "Ultra-Fine", "Intelliphase Temp", "Controller Temp", "", "", "", "", "", ""]
        headerArray2 = ["GFX_H Iout Offset", "GFX_H V-Slope Coeff.", "GFX_H V-Slope Offset.", "GFX_L Iout Offset", "GFX _L V-Slope Coeff.", "GFX _L V-Slope Offset.", "CPU Iout Offset", "CPU V-Slope Coeff.", "CPU V-Slope Offset.", "SOC Iout Offset", "SOC V-Slope Coeff.", "SOC V-Slope Offset.", "MEMP Iout Offset", "MEMP V-Slope Coeff.", "MEMP V-Slope Offset.", "", "", "", "", "", ""]
        
        for columnIndex in range (0, 18):
            dmmSheet.write(0, columnIndex, headerArray1[columnIndex], self.headerCellFormat)
            self.summarySheet.write(16, columnIndex, headerArray2[columnIndex], self.headerCellFormat)

    def recordOffsetOnly(self):
        
        target = 10.0
        
        vImon = self.voltMeter.getVoltage(1)
        print ("VIMON is: " + str(vImon))
        imon = self.misc.calculateCurrent(vImon)
        print ("IMON is: " + str(imon))
        readBackLoad = self.misc.readBackLoad()
        offset_Error = (imon - (target + readBackLoad))
        print ("Offset Error Method 3: " + str(offset_Error))
                    
        self.summarySheet.write(timerThread.TweakCell, offset_Error)
                
        print ("")
        self.logFilePointer.write("Offset Error at Min Load: " + str(offset_Error) + "\n")
        print ("Offset Error at Min Load: " + str(offset_Error))
        print ("")
            
        offset = self.dsmcdbg.readOffsetRegister()
        self.logFilePointer.write("Fine offset setting is now: " + str(offset) + "\n")
        print ("Fine offset setting is now: " + str(offset))
        print ("")
            
        return 

    def quitThread(self):
        
#        self.workBook.close()
        self.voltMeter.close()
        print ("..................")
        print ("got to Quit Thread")
        print ("....................")
        
#        if self.logFile:
#            self.logFilePointer.close()
        
        self.misc.loadOff()
                
