#loadObject is either a VISA resource or a TCP/IP resource
#GIT Version

def setLoad(loadObject, loadNumber, loadValue):
    tempString = "CHAN:LOAD " + str(loadNumber)
    loadObject.write(tempString)
    loadObject.write("CURR:STAT:L1 0\n")
    loadObject.write("CONFigure:AUTO:ON 0\n")
    loadObject.write("CHANnel:ACTive 1\n")
    tempString = "CURR:STAT:L1 " + str(loadValue) 
    loadObject.write(tempString)
    
def setDynamicTimes(loadObject, channel, timeOne, timeTwo):
    tempString = "CHAN:LOAD " + str(channel)
    loadObject.write(tempString)
    
    loadObject.write("CURR:DYN:T1 " + str(timeOne) + "ms\n")
    loadObject.write("CURR:DYN:T2 " + str(timeTwo) + "ms\n")
    
def setDynamicLoads(loadObject, channel, loadOne, loadTwo):
    tempString = "CHAN:LOAD " + str(channel)
    loadObject.write(tempString)
    
    loadObject.write("CURR:DYN:L1 " + str(loadOne) + "A\n")
    loadObject.write("CURR:DYN:L2 " + str(loadTwo) + "A\n")
    
    setSlewRates(loadObject,channel,"MAX","MAX")

def setDynamicLoadPoint(loadObject, channel, load1, load2, time1, time2):
    setDynamicLoads(loadObject, channel, load1, load2)
    setDynamicTimes(loadObject, channel, time1, time2)

#to-do add exceptions for when below 0 or above max of chroma module
def setSlewRates(loadObject, channel, riseSlew, fallSlew):
    tempString = "CHAN:LOAD " + str(channel)
    loadObject.write(tempString)
    
    loadObject.write("CURR:DYN:RISE " + str(riseSlew) + "\n")
    loadObject.write("CURR:DYN:FALL " + str(fallSlew) + "\n")
    
    
def setMode(loadObject, channel, mode, rangeSetting):
    tempString = "CHAN: LOAD " + str(channel)
    loadObject.write(tempString)
    
    if rangeSetting.lower() == "lo" or rangeSetting.lower() == "low":
        rangeDes = "L"
    elif rangeSetting.lower() == "med":
        rangeDes = "M"
    elif rangeSetting.lower() == "hi" or rangeSetting.lower() == "high":
        rangeDes = "H"
    
    if str(mode).lower() == "cc":
        loadObject.write("MODE CC" + rangeDes + "\n")
    elif str(mode).lower() == "ccd":
        loadObject.write("MODE CCD" + rangeDes + "\n")
#        
    
#def setMode(loadObject, channel, mode):
#    tempString = "CHAN: LOAD " + str(channel)
#    loadObject.write(tempString)
#    
#    if mode.lower() == "cch":
#        tempString = "MODE CCH"
#    elif mode.lower() == "ccm":
#        tempString = "MODE CCM"
#    elif mode.lower() == "ccl":
#        tempString = "MODE CCL"
#    elif mode.lower() == "ccdh":
#        tempString = "MODE CCDH"
#    elif mode.lower() == "ccdm":
#        tempString = "MODE CCDM"
#    elif mode.lower() == "ccdl":
#        tempString = "MODE CCDL"
#    loadObject.write(tempString)
        
        
def setLoadOn(loadObject, channel):
    tempString = "CHAN:LOAD " + str(channel)
    loadObject.write(tempString)
    tempString = "LOAD:STATe ON\n" 
    loadObject.write(tempString)
    
def setLoadOff(loadObject, channel):
    tempString = "CHAN:LOAD " + str(channel)
    loadObject.write(tempString)
    tempString = "LOAD:STATe OFF\n" 
    loadObject.write(tempString)
    
def setAllRun(loadObject, channel, enable):
    tempString = "CHAN:LOAD " + str(channel)
    loadObject.write(tempString)
    if enable:
        tempString = "CONFigure:ALLRun ON\n"
        loadObject.write(tempString)
    else:
        tempString = "CONFigure:ALLRun OFF\n"
        loadObject.write(tempString)
    
#def setRangeHiMedLo(loadObject, channel, hiMedLo):
#    loadString = "CHAN:LOAD " + str(channel)
#    loadObject.write(loadString)
#    currentMode = self.mode + " "
#    if hiMedLo.lower() == "hi":
#        loadObject.write("MODE CCH\n")
#    elif hiMedLo.lower() == "med":
#        loadObject.write("MODE CCM\n")
#    elif hiMedLo.lower() == "lo":
#        loadObject.write("MODE CCL\n")
        
def fetchVoltage(loadObject, channel):
    tempString = "CHAN:LOAD " + str(channel)
    loadObject.write(tempString)
    voltage = str(loadObject.query("FETCh:VOLTage?"))
    return voltage
    
def fetchCurrent(loadObject, channel):
    tempString = "CHAN:LOAD " + str(channel)
    loadObject.write(tempString)
    voltage = str(loadObject.query("FETCh:CURRent?"))
    return voltage

  