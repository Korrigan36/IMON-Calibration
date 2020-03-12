# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 08:51:30 2019

@author: v-stpur
"""
import time
import DMMLib
import nidaqmx
import nidaqmx.system
import timerThread

from nidaqmx.constants import (
    AcquisitionType, DigitalWidthUnits, Edge,
    ACExcitWireMode, AccelChargeSensitivityUnits, AccelSensitivityUnits,
    AccelUnits, AngleUnits, BridgeConfiguration, BridgeElectricalUnits,
    BridgePhysicalUnits, BridgeUnits, CJCSource, ChargeUnits,
    CurrentShuntResistorLocation, CurrentUnits,
    EddyCurrentProxProbeSensitivityUnits, ExcitationSource,
    ForceIEPESensorSensitivityUnits, ForceUnits, FrequencyUnits,
    LVDTSensitivityUnits, LengthUnits, PressureUnits, RTDType,
    RVDTSensitivityUnits, ResistanceConfiguration, ResistanceUnits,
    SoundPressureUnits, StrainGageBridgeType, StrainGageRosetteType,
    StrainUnits, TEDSUnits, TemperatureUnits, TerminalConfiguration,
    ThermocoupleType, TorqueUnits, VelocityIEPESensorSensitivityUnits,
    VelocityUnits, VoltageUnits)

class GetVoltage(object):

#    def __init__(self, DMM, adInstr, vreg, scsiCB):
    def __init__(self):
        self.dmm            = timerThread.DMM
        self.adInstr        = timerThread.AdInstr
        self.vregUnderTest  = timerThread.VregUnderTest
#        self.scsiCB         = timerThread.ScsiCB
        
        if self.adInstr == "DMM":
            print ("Set Up DMM")
            self.defaultDmmConfig()
        else:
            self.niDeviceName = self.dmm
            print ("Set up NI Instrument")
            print (self.adInstr)
            #Set up NI Task
            self.taskGFX    = nidaqmx.Task() 
            self.taskCPU    = nidaqmx.Task() 
            self.taskMEMIO  = nidaqmx.Task() 
            self.taskMEMPHY = nidaqmx.Task() 
            self.taskSOC    = nidaqmx.Task() 
            
            self.taskGFX_Sense    = nidaqmx.Task() 
            self.taskCPU_Sense    = nidaqmx.Task() 
            self.taskMEMPHY_Sense = nidaqmx.Task() 
            self.taskSOC_Sense    = nidaqmx.Task() 
            
            if True:
                #VIMON
                self.taskGFX.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai67", max_val=2, min_val=-2, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskCPU.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai66", max_val=2, min_val=-2, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskMEMIO.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai64", max_val=1, min_val=-1, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskMEMPHY.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai65", max_val=2, min_val=-2, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskSOC.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai53", max_val=2, min_val=-2, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                #V Sense
                self.taskGFX_Sense.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai52", max_val=2, min_val=-2, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskCPU_Sense.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai51", max_val=2, min_val=-2, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskMEMPHY_Sense.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai49", max_val=2, min_val=-2, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskSOC_Sense.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai50", max_val=2, min_val=-2, terminal_config = TerminalConfiguration.DIFFERENTIAL)
            else:
                self.taskGFX.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai0", max_val=1, min_val=-1, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskCPU.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai1", max_val=1, min_val=-1, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskMEMIO.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai2", max_val=1, min_val=-1, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskMEMPHY.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai3", max_val=1, min_val=-1, terminal_config = TerminalConfiguration.DIFFERENTIAL)
                self.taskSOC.ai_channels.add_ai_voltage_chan(self.niDeviceName + "/ai4", max_val=1, min_val=-1, terminal_config = TerminalConfiguration.DIFFERENTIAL)

            self.taskGFX.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 50000)
            self.taskCPU.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 50000)
            self.taskMEMIO.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 50000)
            self.taskMEMPHY.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 50000)
            self.taskSOC.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 50000)
            
            self.taskGFX_Sense.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 50000)
            self.taskCPU_Sense.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 50000)
            self.taskMEMPHY_Sense.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 50000)
            self.taskSOC_Sense.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 50000)
            
#            self.taskGFX.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 100000)
#            self.taskCPU.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 100000)
#            self.taskMEMIO.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 100000)
#            self.taskMEMPHY.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 100000)
#            self.taskSOC.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 100000)
#            
#            self.taskGFX_Sense.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 100000)
#            self.taskCPU_Sense.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 100000)
#            self.taskMEMPHY_Sense.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 100000)
#            self.taskSOC_Sense.timing.cfg_samp_clk_timing(100000, "", Edge.RISING, AcquisitionType.FINITE, 100000)
#            
            clkRate = self.taskGFX.timing.samp_quant_samp_mode
            print ("Sample Quant Mode is: " + str(clkRate))
            clkRate = self.taskGFX.timing.samp_quant_samp_per_chan
            print ("Sample Quant Per Chan is: " + str(clkRate))
            clkRate = self.taskGFX.timing.ai_conv_rate
            print ("Convert Rate is: " + str(clkRate))
            clkRate = self.taskGFX.timing.samp_clk_rate
            print ("Clock Rate is: " + str(clkRate))


    def getVoltage(self, averageRuns):
        
        if self.adInstr == "DMM":
            DMMLib.dmm_ArmTrigger(self.dmm)
            DMMLib.dmm_TriggerDevice(self.dmm)
            time.sleep(1)
            dmmVoltage = DMMLib.dmm_GetAverage(self.dmm)
            DMMLib.dmm_DeviceClear(self.dmm)
            vImon = float(dmmVoltage)
        else:
            dataSum = 0
            for outerIndex in range (0,averageRuns):
                
#                if self.vregUnderTest == "GFX":
#                    data = self.taskGFX.read(number_of_samples_per_channel=100000)
#                elif self.vregUnderTest == "CPU":
#                    data = self.taskCPU.read(number_of_samples_per_channel=100000)
#                elif self.vregUnderTest == "MEMIO":
#                    data = self.taskMEMIO.read(number_of_samples_per_channel=100000)
#                elif self.vregUnderTest == "MEMPHY":
#                    data = self.taskMEMPHY.read(number_of_samples_per_channel=100000)
#                elif self.vregUnderTest == "SOC":
#                    data = self.taskSOC.read(number_of_samples_per_channel=100000)
#                    
#                for sumIndex in range (0,100000-1):
#                    dataSum = dataSum + float(data[sumIndex]) 
#                  
#            dataFloat = dataSum / (averageRuns * 100000)
#            vImon = dataFloat

                if self.vregUnderTest == "GFX":
                    data = self.taskGFX.read(number_of_samples_per_channel=50000)
                elif self.vregUnderTest == "CPU":
                    data = self.taskCPU.read(number_of_samples_per_channel=50000)
                elif self.vregUnderTest == "MEMIO":
                    data = self.taskMEMIO.read(number_of_samples_per_channel=50000)
                elif self.vregUnderTest == "MEMPHY":
                    data = self.taskMEMPHY.read(number_of_samples_per_channel=50000)
                elif self.vregUnderTest == "SOC":
                    data = self.taskSOC.read(number_of_samples_per_channel=50000)
                    
                for sumIndex in range (0,50000-1):
                    dataSum = dataSum + float(data[sumIndex]) 
                  
            dataFloat = dataSum / (averageRuns * 50000)
            vImon = dataFloat

        print ("Actual VIMON is: " + str(vImon))
        return vImon
    
    def getVout(self, averageRuns):
        
        if self.adInstr == "DMM":
            print ("V Sense not supported by DMM")
        else:
            dataSum = 0
            for outerIndex in range (0,averageRuns):
                
#                if self.vregUnderTest == "GFX":
#                    data = self.taskGFX_Sense.read(number_of_samples_per_channel=100000)
#                elif self.vregUnderTest == "CPU":
#                    data = self.taskCPU_Sense.read(number_of_samples_per_channel=100000)
#                elif self.vregUnderTest == "MEMIO":
#                    "V Sense not supported for MEMIO"
#                elif self.vregUnderTest == "MEMPHY":
#                    data = self.taskMEMPHY_Sense.read(number_of_samples_per_channel=100000)
#                elif self.vregUnderTest == "SOC":
#                    data = self.taskSOC_Sense.read(number_of_samples_per_channel=100000)
#                    
#                for sumIndex in range (0,100000-1):
#                    dataSum = dataSum + float(data[sumIndex]) 
#                  
#            dataFloat = dataSum / (averageRuns * 100000)
#            vOut = dataFloat

                if self.vregUnderTest == "GFX":
                    data = self.taskGFX_Sense.read(number_of_samples_per_channel=50000)
                elif self.vregUnderTest == "CPU":
                    data = self.taskCPU_Sense.read(number_of_samples_per_channel=50000)
                elif self.vregUnderTest == "MEMIO":
                    "V Sense not supported for MEMIO"
                elif self.vregUnderTest == "MEMPHY":
                    data = self.taskMEMPHY_Sense.read(number_of_samples_per_channel=50000)
                elif self.vregUnderTest == "SOC":
                    data = self.taskSOC_Sense.read(number_of_samples_per_channel=50000)
                    
                for sumIndex in range (0,50000-1):
                    dataSum = dataSum + float(data[sumIndex]) 
                  
            dataFloat = dataSum / (averageRuns * 50000)
            vOut = dataFloat

        print ("Output Voltage is: " + str(vOut))
        return vOut

    def defaultDmmConfig(self):

        DMMLib.dmm_ConfigureDCVoltage(self.dmm, "MIN", "MAX")

    def close(self):
        self.taskGFX.close()
        self.taskCPU.close()
        self.taskMEMIO.close()
        self.taskMEMPHY.close()
        self.taskSOC.close()
