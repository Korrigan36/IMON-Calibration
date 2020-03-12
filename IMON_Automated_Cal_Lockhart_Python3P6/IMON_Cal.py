# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 09:51:31 2017

@author: v-stpurc
"""
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QRadioButton, QVBoxLayout, QCheckBox, QProgressBar,
    QGroupBox, QComboBox, QLineEdit, QPushButton, QMessageBox, QInputDialog, QDialog, QDialogButtonBox, QSlider, QGridLayout, QHBoxLayout)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication, QThread, pyqtSignal
#Low Current
sys.path.append("C:\\Users\\v-stpur\\Documents\\XBoxScripts\\instrument_Libraries\\")

import visa
import timerThread
import dutInfoDialog
import nidaqmx
import nidaqmx.system
import ftd2xx as ftd
import xlsxwriter
import datetime
from dsmcdbgFunctions import DsmcdbgFunctions
import subprocess

version_Info = "Python PyQt5 Lockhart IMON Automated Calibration V1.1"

class MainWindow(QWidget):

    DMM = 0
    Load = 0

    configID = 0
    pcbaSN = 0
    productSN = 0
    runNotes = 0 
    vregText = 0 
    vregSelection = 0
    vregUnderTest = ""
#    scopeShot_Signal = pyqtSignal(str)
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.FTDIsn = self.getFTDIserialNumber()
        print (self.FTDIsn)
        self.logFilePointer = open("CalibrationLog_" + self.FTDIsn + ".txt", "w")
        self.logFilePointer.write("Calibration Run Log File\n")
 
        self.initUI()
        self.setParameters()
        self.openInstruments()
        
        d = ftd.open(0)  
        deviceList = d.getDeviceInfo()
        self.deviceSerialNum = deviceList['serial']
        d.close()

        self.excelFileName = "SCB_IMON_Cal_" + str(self.deviceSerialNum) + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M") + ".xlsx"
        self.workBook = xlsxwriter.Workbook(self.excelFileName)
        self.SummarySheet = self.workBook.add_worksheet("Summary")
        self.PlotSheet = self.workBook.add_worksheet("Plots")
        self.LogSheet = self.workBook.add_worksheet("Log")
       
        self.headerCellFormat = self.workBook.add_format()
        self.headerCellFormat.set_font_size(16)
        self.headerCellFormat.set_bold()
        
        self.logFilePointer.write("FTDI Serial Number " + self.FTDIsn + "\n")
        self.SummarySheet.write(0, 0, "FTDI S.N.", self.headerCellFormat)
        self.SummarySheet.write(0, 1, self.FTDIsn)
        self.SummarySheet.write(0, 2, "DFlash S.N.", self.headerCellFormat)
        self.SummarySheet.write(0, 4, "FW Version", self.headerCellFormat)
        self.SummarySheet.write(0, 6, "Register Check", self.headerCellFormat)
        dflashSN = self.FTDIsn[:-1]
        self.SummarySheet.write(0, 3, dflashSN)
        self.SummarySheet.write(1, 0, "Board Product S.N.", self.headerCellFormat)
        self.SummarySheet.write(1, 2, "Date", self.headerCellFormat)
        
        self.doDutInfo = True

#        print self.flashBoard()
        version = self.getVersion()
        print (version[29:41])
        self.SummarySheet.write(0, 5, version[29:41])

    def initUI(self):
        
        self.setGeometry(300, 300, 600, 200)
        self.setWindowTitle('VIMON Lockhart Calibration')
        self.setWindowIcon(QIcon('xbox_icon.ico')) 
        
        instrumentGroupBox  = QGroupBox()
        instrumentGrid      = QGridLayout()
        switchLabel = QLabel(self)
        switchLabel.setText("Chroma Load")
        instrumentGrid.addWidget(switchLabel, 0, 0)
#        instrumentGrid.setRowMinimumHeight(0, 10)
    
        instrumentChoiceGroupBox  = QGroupBox()
        instrumentChoiceLayout    = QHBoxLayout()

        loadLabel = QLabel(self)
        loadLabel.setText("Voltmeter")
#        instrumentGrid.addWidget(loadLabel, 1, 0)
        instrumentChoiceLayout.addWidget(loadLabel)
  
        self.voltmeterIDN = QLabel(self)
        self.voltmeterIDN.setText("DMM")
#        instrumentGrid.addWidget(self.voltmeterIDN, 1, 1)
        instrumentChoiceLayout.addWidget(self.voltmeterIDN)
    
        self.loadIDN = QLabel(self)
        self.loadIDN.setText("Chroma Load")
        instrumentGrid.addWidget(self.loadIDN, 0, 1)
        instrumentGroupBox.setLayout(instrumentGrid)

        instrumentGroupBox.setLayout(instrumentGrid)
        self.adInstr = "NI"
        
        instrumentChoiceGroupBox.setLayout(instrumentChoiceLayout)
         
        startButtonGroupBox  = QGroupBox()
        startButtonLayout    = QHBoxLayout()
        self.startStopButton = QPushButton('Start Cal', self)
        self.startStopButton.setGeometry(800, 70, 180, 50)

        self.font = QFont()
        self.font.setBold(True)
        self.font.setPointSize(16)
        self.startStopButton.setFont(self.font)
        self.startStopButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: black;}')
        self.startStopButton.setText("Start Cal")
        self.startStopButton.clicked[bool].connect(self.startStopTest)
        startButtonLayout.addWidget(self.startStopButton)
        startButtonGroupBox.setLayout(startButtonLayout)
 
        quitButtonGroupBox  = QGroupBox()
        quitButtonLayout    = QHBoxLayout()
        self.font.setPointSize(12)
        self.quitButton = QPushButton('Quit', self)
        self.quitButton.setFont(self.font)
        self.quitButton.setGeometry(890, 260, 100, 30)
        self.quitButton.clicked[bool].connect(self.closeEventLocal)
        quitButtonLayout.addWidget(self.quitButton)
        quitButtonGroupBox.setLayout(quitButtonLayout)
        
        vregGroupBox = QGroupBox()
        kcsGroupBox = QGroupBox()
        gainGroupBox = QGroupBox()
        rimonGroupBox = QGroupBox()
        tdcGroupBox = QGroupBox()
        minLoadGroupBox = QGroupBox()
        vregGrid = QGridLayout()

        vregLayout = QHBoxLayout()
        self.vregLabel = QLabel(self)
        self.vregLabel.setText("Vreg")
        vregLayout.addWidget(self.vregLabel)
		
        self.b1 = QRadioButton("GFX")
#        self.b1.setChecked(True)
#        self.vregUnderTest = self.b1.text()
        self.b1.toggled.connect(lambda:self.btnstate(self.b1))
        vregLayout.addWidget(self.b1)
		
        self.b2 = QRadioButton("CPU")
#        self.b2.setChecked(True)
#        self.vregUnderTest = self.b2.text()
        self.b2.toggled.connect(lambda:self.btnstate(self.b2))
        vregLayout.addWidget(self.b2)
        
        self.b3 = QRadioButton("MEMPHY")
        self.b3.setChecked(True)
        self.vregUnderTest = self.b3.text()
        self.b3.toggled.connect(lambda:self.btnstate(self.b3))
        vregLayout.addWidget(self.b3)
        
        self.b4 = QRadioButton("MEMIO")
#        self.b4.setChecked(True)
#        self.vregUnderTest = self.b4.text()
#        self.b4.toggled.connect(lambda:self.btnstate(self.b4))
#        vregLayout.addWidget(self.b4)
        
        self.b5 = QRadioButton("SOC")
#        self.b5.setChecked(True)
#        self.vregUnderTest = self.b5.text()
        self.b5.toggled.connect(lambda:self.btnstate(self.b5))
        vregLayout.addWidget(self.b5)
        
        vregGroupBox.setLayout(vregLayout)

        kcsLayout = QHBoxLayout()
		
        self.kcsLabel = QLabel(self)
        self.kcsLabel.setText("Kcs")
        kcsLayout.addWidget(self.kcsLabel)
		
        self.gfxKcs = QLineEdit(self)
        self.gfxKcs.setText("9.7")
        kcsLayout.addWidget(self.gfxKcs)

        self.cpuKcs = QLineEdit(self)
        self.cpuKcs.setText("8.7")
        kcsLayout.addWidget(self.cpuKcs)
        
        self.memphyKcs = QLineEdit(self)
        self.memphyKcs.setText("10.0")
        kcsLayout.addWidget(self.memphyKcs)
        
        self.socKcs = QLineEdit(self)
        self.socKcs.setText("10.0")
        kcsLayout.addWidget(self.socKcs)
        
        kcsGroupBox.setLayout(kcsLayout)

        gainLayout = QHBoxLayout()
        self.gainLabel = QLabel(self)
        self.gainLabel.setText("Gain")
        gainLayout.addWidget(self.gainLabel)

        self.gfxGain = QLineEdit(self)
        self.gfxGain.setText("8.0")
        gainLayout.addWidget(self.gfxGain)
		
        self.cpuGain = QLineEdit(self)
        self.cpuGain.setText("8.0")
        gainLayout.addWidget(self.cpuGain)
        
        self.memphyGain = QLineEdit(self)
        self.memphyGain.setText("16.0")
        gainLayout.addWidget(self.memphyGain)
        
        self.socGain = QLineEdit(self)
        self.socGain.setText("16.0")
        gainLayout.addWidget(self.socGain)
        
        gainGroupBox.setLayout(gainLayout)

        rimonLayout = QHBoxLayout()
        self.rimonLabel = QLabel(self)
        self.rimonLabel.setText("Rimon")
        rimonLayout.addWidget(self.rimonLabel)

        self.gfxRimon = QLineEdit(self)
        self.gfxRimon.setText("10.0")
        rimonLayout.addWidget(self.gfxRimon)
		
        self.cpuRimon = QLineEdit(self)
        self.cpuRimon.setText("10.0")
        rimonLayout.addWidget(self.cpuRimon)
        
        self.memphyRimon = QLineEdit(self)
        self.memphyRimon.setText("40.0")
        rimonLayout.addWidget(self.memphyRimon)
        
        self.socRimon = QLineEdit(self)
        self.socRimon.setText("40.0")
        rimonLayout.addWidget(self.socRimon)
        
        rimonGroupBox.setLayout(rimonLayout)

        tdcLayout = QHBoxLayout()
        self.tdcLabel = QLabel(self)
        self.tdcLabel.setText("TDC")
        tdcLayout.addWidget(self.tdcLabel)

        self.gfxTdc = QLineEdit(self)
        self.gfxTdc.setText("90.0")
        tdcLayout.addWidget(self.gfxTdc)
		
        self.cpuTdc = QLineEdit(self)
        self.cpuTdc.setText("50.0")
        tdcLayout.addWidget(self.cpuTdc)
        
        self.memphyTdc = QLineEdit(self)
        self.memphyTdc.setText("12.0")
        tdcLayout.addWidget(self.memphyTdc)
        
        self.socTdc = QLineEdit(self)
        self.socTdc.setText("40.0")
        tdcLayout.addWidget(self.socTdc)
        
        tdcGroupBox.setLayout(tdcLayout)

        minLoadLayout = QHBoxLayout()
        self.minLoadLabel = QLabel(self)
        self.minLoadLabel.setText("Min Load")
        minLoadLayout.addWidget(self.minLoadLabel)

        self.gfxMinload = QLineEdit(self)
        self.gfxMinload.setText("2.0")
        minLoadLayout.addWidget(self.gfxMinload)
		
        self.cpuMinload = QLineEdit(self)
        self.cpuMinload.setText("1.0")
        minLoadLayout.addWidget(self.cpuMinload)
        
        self.memphyMinload = QLineEdit(self)
        self.memphyMinload.setText("1.0")
        minLoadLayout.addWidget(self.memphyMinload)
        
        self.socMinload = QLineEdit(self)
        self.socMinload.setText("1.0")
        minLoadLayout.addWidget(self.socMinload)
        
        minLoadGroupBox.setLayout(minLoadLayout)

        vregGrid.addWidget(vregGroupBox, 0, 0)
        vregGrid.addWidget(kcsGroupBox, 1, 0)
        vregGrid.addWidget(gainGroupBox, 2, 0)
        vregGrid.addWidget(rimonGroupBox, 3, 0)
        vregGrid.addWidget(tdcGroupBox, 4, 0)
        vregGrid.addWidget(minLoadGroupBox, 5, 0)

        vregGridBox = QGroupBox()
        vregGridBox.setLayout(vregGrid)

        selectionGrid      = QGridLayout()
#        layout2 = QHBoxLayout()
        self.tempCB = QCheckBox("Temperature Sweep")
        selectionGrid.addWidget(self.tempCB, 0, 0)
		
        self.voltCB = QCheckBox("Voltage Sweep")
        selectionGrid.addWidget(self.voltCB, 0, 1)
        
        self.calCB = QCheckBox("Calibration Sweep")
        selectionGrid.addWidget(self.calCB, 0, 2)
        self.calCB.setChecked(True)

        self.bitWeightCB = QCheckBox("Bit Weight")
        selectionGrid.addWidget(self.bitWeightCB, 1, 0)
        
        self.vimonCB = QCheckBox("VIMON Average")
        selectionGrid.addWidget(self.vimonCB, 1, 1)

        self.loadCB = QCheckBox("Load Sweep")
        selectionGrid.addWidget(self.loadCB, 1, 2)

        self.logCB = QCheckBox("Create Log File")
        selectionGrid.addWidget(self.logCB, 2, 0)

        self.lockhartCB = QCheckBox("Lockhart Board")
        selectionGrid.addWidget(self.lockhartCB, 2, 1)
        self.lockhartCB.setChecked(False)
        self.lockhartCB.toggled.connect(self.setParameters)

        self.lowCurrentCB = QCheckBox("Low Current GFX")
        selectionGrid.addWidget(self.lowCurrentCB, 2, 2)
        self.lowCurrentCB.setChecked(False)
        self.lowCurrentCB.setEnabled(False)
        self.lowCurrentCB.toggled.connect(self.setParameters)

        selectionGroupBox  = QGroupBox()
        selectionGroupBox.setLayout(selectionGrid)

        grid = QGridLayout()
        grid.setColumnStretch(0,5)
        grid.setColumnStretch(1,5)
        grid.addWidget(instrumentGroupBox, 0, 0)
        grid.addWidget(instrumentChoiceGroupBox, 0, 1)
        grid.addWidget(vregGridBox, 1, 0)
        grid.addWidget(selectionGroupBox, 1, 1)
        grid.addWidget(startButtonGroupBox, 2, 0)
        grid.addWidget(quitButtonGroupBox, 2, 1)
        self.setLayout(grid)

        self.show()

    def btnstate(self,b):
      
        if b.text() == "GFX":
            if b.isChecked() == True:
                print (b.text() +" is selected")
                self.vregUnderTest = b.text()
        elif b.text() == "CPU":
            if b.isChecked() == True:
                print (b.text() +" is selected")
                self.vregUnderTest = b.text()
        elif b.text() == "MEMPHY":
            if b.isChecked() == True:
                print (b.text() +" is selected")
                self.vregUnderTest = b.text()
        elif b.text() == "MEMIO":
            if b.isChecked() == True:
                print (b.text() +" is selected")
                self.vregUnderTest = b.text()
        elif b.text() == "MEMPHY":
            if b.isChecked() == True:
                print (b.text() +" is selected")
                self.vregUnderTest = b.text()
        elif b.text() == "SOC":
            if b.isChecked() == True:
                print (b.text() +" is selected")
                self.vregUnderTest = b.text()
        
    def closeEventLocal(self, event):
        try:
            self.work.stopTimer()
        except:
            print ("Timer Thread Not Running got to here")
            
        self.readRegisters()

        self.logFilePointer.close()
        self.logFilePointer = open("CalibrationLog_" + self.FTDIsn + ".txt", "r")
        logData = self.logFilePointer.read()
        options = {'width': 350,'height': 28000,}
#        self.LogSheet.insert_textbox(2, 2, logData, options)
        self.LogSheet.insert_textbox(2, 2, logData, options)
        self.workBook.close()
#        self.thread.quit()
        print("Got quit signal")
#        self.work.stopTimer()
#        self.thread.wait()
        self.logFilePointer.close()
        
        self.close()

    def runLoop(self, stepCount):
        self.progressBar.setValue(int(stepCount))

    def quitLoop(self):
        
        global countGFXruns
        
        self.startStopButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: black;}')
        self.startStopButton.setText("Start Cal")
        sys.stdout.write('\a')
        sys.stdout.flush()
        
        if self.calCB.isChecked():
            self.calCB.setChecked(False)
            self.voltCB.setChecked(True)
            self.loadCB.setChecked(False)
        elif self.voltCB.isChecked():
            self.calCB.setChecked(False)
            self.voltCB.setChecked(False)
            self.loadCB.setChecked(True)
        elif self.loadCB.isChecked():
            self.calCB.setChecked(True)
            self.voltCB.setChecked(False)
            self.loadCB.setChecked(False)
            if self.b1.isChecked() and (not self.lowCurrentCB.isChecked()) and (not self.lockhartCB.isChecked()):
                self.b1.setChecked(True)  
                self.lowCurrentCB.setChecked(True)
                self.b2.setChecked(False)    
                self.b3.setChecked(False)    
                self.b5.setChecked(False)    
            elif (self.b1.isChecked() and self.lowCurrentCB.isChecked()) or (self.b1.isChecked() and self.lockhartCB.isChecked()):
                self.b1.setChecked(False)    
                self.b2.setChecked(False)    
                self.b3.setChecked(True)    
                self.lowCurrentCB.setChecked(False)
                self.b5.setChecked(False)    
            elif self.b2.isChecked():
                self.b1.setChecked(True)    
                self.b2.setChecked(False)    
                self.b3.setChecked(False)    
                self.b5.setChecked(False)    
            elif self.b3.isChecked():
                self.b1.setChecked(False)    
                self.b2.setChecked(False)    
                self.b3.setChecked(False)    
                self.b5.setChecked(True)    
            elif self.b5.isChecked():
                self.b1.setChecked(False)    
                self.b2.setChecked(True)    
                self.b3.setChecked(False)    
                self.b5.setChecked(False)    

                
        self.thread.quit()

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False   
        
    def startStopTest(self):
        returnString = self.startStopButton.text()
        if returnString.find("Start Cal") != -1:
        
            #Only Do this Once
            if self.doDutInfo:
                dialog = dutInfoDialog.DutInfoDialog()
                dialog.setWindowModality(Qt.ApplicationModal)
                dialog.exec_()
                self.configID, self.pcbaSN, self.productSN, self.runNotes = dialog.returnInfo()
                self.doDutInfo = False
 
            print ("Test Started")

            self.startStopButton.setStyleSheet('QPushButton {background-color: #FF2000; color: black;}')
            self.startStopButton.font()
            self.startStopButton.setText("Abort Cal")
            
            self.startThread()
           
        else:
            print ("Test Aborted")
            self.startStopButton.setStyleSheet('QPushButton {background-color: #A3C1DA; color: black;}')
            self.startStopButton.setText("Start Cal")

            self.thread.quit()
            self.work.stopTimer()

    def startThread(self):
        
        self.adInstr = "NI"
        
        if self.lockhartCB.isChecked():
            self.logFilePointer.write("Lockhart Board\n")
        else:
            self.logFilePointer.write("Anaconda Board\n")
            if self.lowCurrentCB.isChecked():
                self.logFilePointer.write("Low Current Mode\n")
            else:
                self.logFilePointer.write("High Current Mode\n")
        self.logFilePointer.write("GFX Kcs " + self.gfxKcs.text() + "\n")
        self.logFilePointer.write("GFX Gain " + self.gfxGain.text() + "\n")
        self.logFilePointer.write("GFX Rimon " + self.gfxRimon.text() + "\n")
        self.logFilePointer.write("GFX TDC " + self.gfxTdc.text() + "\n")
        self.logFilePointer.write("CPU Kcs " + self.cpuKcs.text() + "\n")
        self.logFilePointer.write("CPU Gain " + self.cpuGain.text() + "\n")
        self.logFilePointer.write("CPU Rimon " + self.cpuRimon.text() + "\n")
        self.logFilePointer.write("CPU TDC " + self.cpuTdc.text() + "\n")
        self.logFilePointer.write("Memphy Kcs " + self.memphyKcs.text() + "\n")
        self.logFilePointer.write("Memphy Gain " + self.memphyGain.text() + "\n")
        self.logFilePointer.write("Memphy Rimon " + self.memphyRimon.text() + "\n")
        self.logFilePointer.write("Memphy TDC " + self.memphyTdc.text() + "\n")
        self.logFilePointer.write("SOC Kcs " + self.socKcs.text() + "\n")
        self.logFilePointer.write("SOC Gain " + self.socGain.text() + "\n")
        self.logFilePointer.write("SOC Rimon " + self.socRimon.text() + "\n")
        self.logFilePointer.write("SOC TDC " + self.socTdc.text() + "\n")

        parameterArray = [self.Load, self.DMM, self.adInstr, self.vimonCB.isChecked(),  self.bitWeightCB.isChecked(), self.tempCB.isChecked(), self.voltCB.isChecked(), self.calCB.isChecked(), self.loadCB.isChecked(), self.logFilePointer, 
                          self.lockhartCB.isChecked(), self.lowCurrentCB.isChecked(), self.vregUnderTest, self.configID, self.pcbaSN, self.productSN, self.runNotes, self.workBook, self.SummarySheet, self.PlotSheet,
                          self.gfxKcs.text(), self.cpuKcs.text(), self.memphyKcs.text(), self.socKcs.text(), self.gfxGain.text(), self.cpuGain.text(), self.memphyGain.text(), self.socGain.text(),
                          self.gfxRimon.text(), self.cpuRimon.text(), self.memphyRimon.text(), self.socRimon.text(), self.gfxTdc.text(), self.cpuTdc.text(), self.memphyTdc.text(), self.socTdc.text(),
                          self.gfxMinload.text(), self.cpuMinload.text(), self.memphyMinload.text(), self.socMinload.text()]

        self.logFilePointer.write("Starting Thread for " + self.vregUnderTest + "\n")
        self.work = timerThread.TimerThread(parameterArray) 
        self.work.timerSignal.connect(self.runLoop)
        self.work.quitSignal.connect(self.quitLoop)
        self.thread = QThread()

        self.work.moveToThread(self.thread)
        self.thread.started.connect(self.work.run)
        self.thread.start()
      
    def openInstruments(self):
        rm = visa.ResourceManager()
        instrumentList = {}
        instrumentList = rm.list_resources()
        
#        print instrumentList
        for loopIndex in range(0, len(instrumentList)):
            
            inst = rm.open_resource(instrumentList[loopIndex])
            try:
                returnString = inst.query("*IDN?")
                print (returnString)
                if returnString.find("CHROMA,63600") != -1:
                    print("found chroma")
                    self.Load = inst
                    self.loadIDN.setText(returnString[:12])
                if instrumentList[loopIndex][7:9] == '22':
                    print ("found DMM 22")
                    inst = rm.open_resource(instrumentList[loopIndex])
                    returnString = inst.query("*IDN?")
                    print (returnString)
                    tempInst = inst
                    tempString = returnString[:11]
#                    self.voltmeterIDN.setText(returnString)
            except visa.VisaIOError:
                print ("bad juju in instrument list")
                
        system = nidaqmx.system.System.local()
        system.driver_version
        for device in system.devices:
            self.niDeviceName = system.devices.device_names[0]
            device = system.devices.__getitem__(0)
            print(self.niDeviceName)
#            self.niIDN.setText(self.niDeviceName + ": " + str(device.product_type))
        
        if self.adInstr == "DMM":
            self.voltmeterIDN.setText(tempString)
            self.DMM = tempInst
        elif self.adInstr == "NI":
            self.voltmeterIDN.setText(self.niDeviceName + ": " + str(device.product_type))
            self.DMM = self.niDeviceName

    def getFTDIserialNumber(self):  
        d = ftd.open(0)  
        deviceList = d.getDeviceInfo()
        self.deviceSerialNum = deviceList['serial']
#        self.deviceSerialNum = self.deviceSerialNum[:0] 
        print ("FTDI Serial Number is: " + str(self.deviceSerialNum))
        d.close()
        return str(self.deviceSerialNum)
            
    def flashBoard(self):
#        p = subprocess.Popen("C:\\Users\\v-stpur\\Documents\\xbtools>sflash.exe /remotefile:smcfw.bin /rawwrite:\\gameshare2\ieb\yukon\Stockton\SMC\images\experimental\Stockton_SMC_10_22_2019_Vreg_0P13\SCB_FAB_B\SMCFW_23_e209_ff.mng", stdout=subprocess.PIPE, shell=False)
        p = subprocess.Popen("C:\\Users\\v-stpur\\Documents\\xbtools>sflash.exe ", stdout=subprocess.PIPE, shell=True)
        returnString = str(p.communicate())
        return returnString
            
    def getVersion(self):
        p = subprocess.Popen("dsmcdbg status -i", stdout=subprocess.PIPE, shell=True)
        returnString = str(p.communicate())
        return returnString

    def readRegisters(self):
        p = subprocess.Popen("dsmcdbg sjm i2c system wr 0x20 0x00 0x01 stop rdword 0x20 0xCA", stdout=subprocess.PIPE, shell=True)
        gainString = str(p.communicate())
        self.SummarySheet.write(0, 7, gainString)
        p = subprocess.Popen("dsmcdbg sjm i2c system wr 0x20 0x00 0x01 stop rdword 0x20 0xCC", stdout=subprocess.PIPE, shell=True)
        gainString = str(p.communicate())
        self.SummarySheet.write(0, 8, gainString)
        p = subprocess.Popen("dsmcdbg sjm i2c system wr 0x20 0x00 0x01 stop rdword 0x20 0xCB", stdout=subprocess.PIPE, shell=True)
        gainString = str(p.communicate())
        self.SummarySheet.write(0, 9, gainString)
        p = subprocess.Popen("dsmcdbg sjm i2c system wr 0x23 0x00 0x01 stop rdword 0x23 0xCA", stdout=subprocess.PIPE, shell=True)
        gainString = str(p.communicate())
        self.SummarySheet.write(0, 10, gainString)
        p = subprocess.Popen("dsmcdbg sjm i2c system wr 0x23 0x00 0x01 stop rdword 0x23 0xCC", stdout=subprocess.PIPE, shell=True)
        gainString = str(p.communicate())
        self.SummarySheet.write(0, 11, gainString)
        
    def setParameters(self):
        
        if self.lockhartCB.isChecked():
            self.lowCurrentCB.setEnabled(False)
            self.gfxKcs.setText("9.7")
            self.cpuKcs.setText("8.7")
            self.memphyKcs.setText("10.0")
            self.socKcs.setText("10.0")
            self.gfxGain.setText("8.0")
            self.cpuGain.setText("8.0")
            self.memphyGain.setText("16.0")
            self.socGain.setText("16.0")
            self.gfxRimon.setText("10.0")
            self.cpuRimon.setText("10.0")
            self.memphyRimon.setText("40.0")
            self.socRimon.setText("40.0")
            self.gfxTdc.setText("90.0")
            self.cpuTdc.setText("50.0")
            self.memphyTdc.setText("12.0")
            self.socTdc.setText("40.0")
            self.gfxMinload.setText("2.0")
            self.cpuMinload.setText("1.0")
            self.memphyMinload.setText("1.0")
            self.socMinload.setText("1.0")
        else:
            self.lowCurrentCB.setEnabled(True)

            if self.lowCurrentCB.isChecked():
                self.gfxKcs.setText("8.7")
                self.gfxGain.setText("8.0")
                self.gfxRimon.setText("10.0")
                self.gfxTdc.setText("63.0")
                self.gfxMinload.setText("2.0")
            else:
                self.gfxKcs.setText("8.7")
                self.gfxGain.setText("16.0")
                self.gfxRimon.setText("5.0")
                self.gfxTdc.setText("260.0")
                self.gfxMinload.setText("2.0")
                
            self.cpuKcs.setText("8.7")
            self.memphyKcs.setText("10.0")
            self.socKcs.setText("8.7")
            
            self.cpuGain.setText("8.0")
            self.memphyGain.setText("16.0")
            self.socGain.setText("16.0")
            
            self.cpuRimon.setText("10.0")
            self.memphyRimon.setText("40.0")
            self.socRimon.setText("40.0")
            
            self.cpuTdc.setText("98.0")
            self.memphyTdc.setText("35.0")
            self.socTdc.setText("50.0")
            
            self.cpuMinload.setText("1.0")
            self.memphyMinload.setText("1.0")
            self.socMinload.setText("1.0")
        

if __name__ == '__main__':
    
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    ex = MainWindow()
    app.exec_()  
#    sys.exit(app.exec_())  
