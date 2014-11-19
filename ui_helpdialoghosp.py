# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_helpdialoghosp.ui'
#
# Created: Mon Jul 21 17:41:46 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
class HelpDialogHospDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
	self.uiHelpHos = Ui_HelpDialogHosp()
        self.uiHelpHos.setupUi(self)
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_HelpDialogHosp(object):
    def setupUi(self, HelpDialogHosp):
        HelpDialogHosp.setObjectName(_fromUtf8("HelpDialogHosp"))
        HelpDialogHosp.resize(682, 487)
        self.tbwHosp = QtGui.QTabWidget(HelpDialogHosp)
        self.tbwHosp.setGeometry(QtCore.QRect(10, 10, 661, 341))
        self.tbwHosp.setObjectName(_fromUtf8("tbwHosp"))
        self.getting_started_tab = QtGui.QWidget()
        self.getting_started_tab.setObjectName(_fromUtf8("getting_started_tab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.getting_started_tab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.getting_started_textIDP = QtGui.QTextEdit(self.getting_started_tab)
        self.getting_started_textIDP.setReadOnly(True)
        self.getting_started_textIDP.setObjectName(_fromUtf8("getting_started_textIDP"))
        self.gridLayout_2.addWidget(self.getting_started_textIDP, 0, 0, 1, 1)
        self.tbwHosp.addTab(self.getting_started_tab, _fromUtf8(""))
        self.findRoutes_tab = QtGui.QWidget()
        self.findRoutes_tab.setObjectName(_fromUtf8("findRoutes_tab"))
        self.gridLayout_3 = QtGui.QGridLayout(self.findRoutes_tab)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.txtHelpIDPa = QtGui.QTextEdit(self.findRoutes_tab)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.txtHelpIDPa.setFont(font)
        self.txtHelpIDPa.setReadOnly(True)
        self.txtHelpIDPa.setObjectName(_fromUtf8("txtHelpIDPa"))
        self.gridLayout_3.addWidget(self.txtHelpIDPa, 0, 0, 1, 1)
        self.tbwHosp.addTab(self.findRoutes_tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.txtHelpIDPa_2 = QtGui.QTextEdit(self.tab_2)
        self.txtHelpIDPa_2.setGeometry(QtCore.QRect(10, 10, 649, 290))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.txtHelpIDPa_2.setFont(font)
        self.txtHelpIDPa_2.setReadOnly(True)
        self.txtHelpIDPa_2.setObjectName(_fromUtf8("txtHelpIDPa_2"))
        self.tbwHosp.addTab(self.tab_2, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.txtHelpIDPa_3 = QtGui.QTextEdit(self.tab)
        self.txtHelpIDPa_3.setGeometry(QtCore.QRect(10, 10, 649, 290))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.txtHelpIDPa_3.setFont(font)
        self.txtHelpIDPa_3.setReadOnly(True)
        self.txtHelpIDPa_3.setObjectName(_fromUtf8("txtHelpIDPa_3"))
        self.tbwHosp.addTab(self.tab, _fromUtf8(""))
        self.about_tab = QtGui.QWidget()
        self.about_tab.setObjectName(_fromUtf8("about_tab"))
        self.gridLayout = QtGui.QGridLayout(self.about_tab)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.about_textIDP = QtGui.QTextEdit(self.about_tab)
        self.about_textIDP.setReadOnly(True)
        self.about_textIDP.setObjectName(_fromUtf8("about_textIDP"))
        self.gridLayout.addWidget(self.about_textIDP, 0, 0, 1, 1)
        self.tbwHosp.addTab(self.about_tab, _fromUtf8(""))
        self.btnCloseHelpIDP = QtGui.QPushButton(HelpDialogHosp)
        self.btnCloseHelpIDP.setGeometry(QtCore.QRect(570, 410, 98, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.btnCloseHelpIDP.setFont(font)
        self.btnCloseHelpIDP.setObjectName(_fromUtf8("btnCloseHelpIDP"))
        self.label_11 = QtGui.QLabel(HelpDialogHosp)
        self.label_11.setGeometry(QtCore.QRect(20, 360, 211, 111))
        self.label_11.setStyleSheet(_fromUtf8("image: url(:/plugins/floogin/a.png);"))
        self.label_11.setText(_fromUtf8(""))
        self.label_11.setObjectName(_fromUtf8("label_11"))

        self.retranslateUi(HelpDialogHosp)
        self.tbwHosp.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(HelpDialogHosp)

    def retranslateUi(self, HelpDialogHosp):
        HelpDialogHosp.setWindowTitle(_translate("HelpDialogHosp", "HelpDialogHosp", None))
        self.getting_started_textIDP.setHtml(_translate("HelpDialogHosp", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\';\">These are the first few steps you need to follow in order to find non-affected IDP camps:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Cantarell\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 1</span> : Load the <span style=\" color:#0000ff;\">flood-hazard layer</span> and <span style=\" color:#0000ff;\">building layer</span> </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 2</span> : Check whether a file with <span style=\" color:#ff0000;\">.keywords</span> extension, is available in each layer bundle </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 3</span> : If (.keywords files) available, press on <span style=\" color:#0000ff;\">Generate map for process</span> button to generate a <span style=\" color:#0000ff;\">IDP-safe</span> layer</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 4</span> : If (.keywords files) <span style=\" color:#ff0000;\">not</span> available, select the <span style=\" color:#0000ff;\">flood-hazard layer</span> and <span style=\" color:#0000ff;\">building layer</span> from the drop downs and provide a name for the output shapefile</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 5</span> : <span style=\" color:#ff0000;\">(If followed step 4)</span> press on <span style=\" color:#0000ff;\">Generate map</span> button to generate a<span style=\" color:#0000ff;\"> Non affected Hospital </span>layer</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 6</span> : The generated <span style=\" color:#0000ff;\">Non affected Hospital</span> layer will be automatically loaded to the TOC and will be saved in your <span style=\" color:#0000ff;\">/home</span> directory </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">    </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.tbwHosp.setTabText(self.tbwHosp.indexOf(self.getting_started_tab), _translate("HelpDialogHosp", "Getting Started", None))
        self.txtHelpIDPa.setHtml(_translate("HelpDialogHosp", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">Follow these instructions in order to Find </span><span style=\" font-family:\'Sans\'; font-size:11pt;\">non-affected Hospitals.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">1</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Load the </span><span style=\" font-size:11pt; color:#0000ff;\">Non affected Hospital</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> map </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">2</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Check on the </span><span style=\" font-size:11pt; color:#0000ff;\">Non affected Hospitals</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">3</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Details of </span><span style=\" font-size:11pt; color:#0000ff;\">Non affected Hospitals</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> will display on th detail tet browser.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">4</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Check on the </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">show all in attribute table</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">5</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Display the Attribute table of </span><span style=\" font-size:11pt; color:#0000ff;\">Non affected Hospital</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> details with the available number of beds.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">6.</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> Total number of Non Affected Hospitals will be displyed in the area.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">7.</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> Click on Print to a text file in order to get details in to a text file.</span></p></body></html>", None))
        self.tbwHosp.setTabText(self.tbwHosp.indexOf(self.findRoutes_tab), _translate("HelpDialogHosp", "Identify Non Affected Hospitals", None))
        self.txtHelpIDPa_2.setHtml(_translate("HelpDialogHosp", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">Follow these instructions in order to Find number of Doctors in  each hospitals</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">1</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Load the </span><span style=\" font-size:11pt; color:#0000ff;\">Non affected Hospital</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> map </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">2</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Check on the </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Number of Registered Doctors</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">3</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Details of </span><span style=\" font-size:11pt; color:#0000ff;\">Non affected Hospitals</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> will display on th detail tet browser.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">4.</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> Display the Attribute table of </span><span style=\" font-size:11pt; color:#0000ff;\">Non affected Hospital</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> details with the available number of Doctors</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">5.</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> Total number of Non Affected Hospitals will be displyed in the area.</span></p></body></html>", None))
        self.tbwHosp.setTabText(self.tbwHosp.indexOf(self.tab_2), _translate("HelpDialogHosp", "Get number of Registered Doctors ", None))
        self.txtHelpIDPa_3.setHtml(_translate("HelpDialogHosp", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">Follow these instructions in order to Find number of Doctors in  each hospitals</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">1</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Load the </span><span style=\" font-size:11pt; color:#0000ff;\">Non affected Hospital</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> map </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">2</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Check on the </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Pharmacies </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#000000;\">to display available non affected pharmacies in the particular area.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">3.</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> Check on the </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Clinics </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#000000;\">to display available non affected </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Clinics</span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#000000;\"> in the particular area.</span></p></body></html>", None))
        self.tbwHosp.setTabText(self.tbwHosp.indexOf(self.tab), _translate("HelpDialogHosp", "Places for Pre Medicinal Needs", None))
        self.about_textIDP.setHtml(_translate("HelpDialogHosp", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#ff0000;\">FLOOgin</span> is a fully automated Free and Open Source tool or a plugin for QGIS (Quantum Geographic Information System) software, which helps to response immediately when a flooding disaster strikes and aims to produce a realistic natural hazard impact scenarios for better planning, preparedness and response activities using hazard and exposure geographic data. </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> consists with impact functions which provides information about</span>, Health Risks (Epidemic diseases), Medicinal resources (Number of medical practitioners, Drugs, Vaccinations, Ambulances), Hospitals with capacities (number of beds) </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> will identify the </span>villages, resource centres (IDP camps), nearby hospitals which has limited road accessibility due to flood.</p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> will identify the </span>best possible<span style=\" font-weight:600;\"> </span>alternative route available to reach affected locations identified above. </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> will help to </span>allocate flood victims to identified resource centres based on available facilities and capacities </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> will</span> generate reports and related maps to above mentioned tools. </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"www.google.com\"><span style=\" text-decoration: underline; color:#0000ff;\">FLOOgin website</span></a> will display simplified outputs of the generated information</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.tbwHosp.setTabText(self.tbwHosp.indexOf(self.about_tab), _translate("HelpDialogHosp", "About FLOOgin", None))
        self.btnCloseHelpIDP.setText(_translate("HelpDialogHosp", "Close", None))

