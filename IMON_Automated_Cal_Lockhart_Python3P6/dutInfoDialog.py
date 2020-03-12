#import sys
from PyQt5.QtWidgets import (QLabel, QLineEdit, QPushButton, QDialog, QGridLayout)
from PyQt5.QtGui import QIcon, QPainter, QPen, QFont
import datetime
#GIT Version

class DutInfoDialog(QDialog):
    def __init__(self):
        super(DutInfoDialog, self).__init__()

        self.initUI()

    def initUI(self):
         
        self.setGeometry(200, 200, 300, 100)
        self.setWindowTitle('DUT Info')
        self.setWindowIcon(QIcon('xbox_icon.ico')) 
        
#        listGroupBox  = QGroupBox()
        listGrid      = QGridLayout()

        configId = QLabel(self)
        configId.setGeometry(10, 10, 80, 20)
        configId.setText("Config ID")
        listGrid.addWidget(configId, 0, 0)
        
        self.configIdLineEdit = QLineEdit(self)
#        self.configIdLineEdit.setGeometry(10, 30, 80, 20)
        self.configIdLineEdit.setText("TEV2SCB-24A")
        listGrid.addWidget(self.configIdLineEdit, 0, 1)

        pcbaSN = QLabel(self)
        pcbaSN.setGeometry(100, 10, 140, 20)
        pcbaSN.setText("PCBA Serial #")
        listGrid.addWidget(pcbaSN, 1, 0)
        
        self.pcbaSNLineEdit = QLineEdit(self)
#        self.pcbaSNLineEdit.setGeometry(100, 30, 300, 20)
        self.pcbaSNLineEdit.setText("")
        listGrid.addWidget(self.pcbaSNLineEdit, 1, 1)

        productSN = QLabel(self)
        productSN.setGeometry(250, 10, 120, 20)
        productSN.setText("Product Serial #")
        listGrid.addWidget(productSN, 2, 0)
        
        self.productSNLineEdit = QLineEdit(self)
        self.productSNLineEdit.setGeometry(250, 30, 300, 20)
        self.productSNLineEdit.setText("n/a")
        listGrid.addWidget(self.productSNLineEdit, 2, 1)

        runNotes = QLabel(self)
        runNotes.setGeometry(200, 55, 150, 20)
        runNotes.setText("Run Notes")
        listGrid.addWidget(runNotes, 3, 0)
        
        self.runNotesLineEdit = QLineEdit(self)
        self.runNotesLineEdit.setGeometry(200, 75, 300, 20)
        self.runNotesLineEdit.setText(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        listGrid.addWidget(self.runNotesLineEdit, 3, 1)

        self.okButton = QPushButton('Ok', self)
        self.okButton.setGeometry(210, 160, 80, 30)
        self.okButton.clicked[bool].connect(self.returnInfo)
        listGrid.addWidget(self.okButton, 4, 1)

        self.setLayout(listGrid)
#        self.show()
       
    def returnInfo(self):
        self.close()
        return (self.configIdLineEdit.text(), self.pcbaSNLineEdit.text(), self.productSNLineEdit.text(), self.runNotesLineEdit.text())

   
