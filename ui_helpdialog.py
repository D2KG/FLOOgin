# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_helpdialog.ui'
#
# Created: Tue Aug 19 14:54:51 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
class helpDialogDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
	self.uiHelp = Ui_helpDialog()
        self.uiHelp.setupUi(self)
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

class Ui_helpDialog(object):
    def setupUi(self, helpDialog):
        helpDialog.setObjectName(_fromUtf8("helpDialog"))
        helpDialog.resize(684, 484)
        self.tbwRoad = QtGui.QTabWidget(helpDialog)
        self.tbwRoad.setGeometry(QtCore.QRect(10, 10, 665, 341))
        self.tbwRoad.setObjectName(_fromUtf8("tbwRoad"))
        self.getting_started_tab = QtGui.QWidget()
        self.getting_started_tab.setObjectName(_fromUtf8("getting_started_tab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.getting_started_tab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.getting_started_text = QtGui.QTextEdit(self.getting_started_tab)
        self.getting_started_text.setReadOnly(True)
        self.getting_started_text.setObjectName(_fromUtf8("getting_started_text"))
        self.gridLayout_2.addWidget(self.getting_started_text, 0, 0, 1, 1)
        self.tbwRoad.addTab(self.getting_started_tab, _fromUtf8(""))
        self.findRoutes_tab = QtGui.QWidget()
        self.findRoutes_tab.setObjectName(_fromUtf8("findRoutes_tab"))
        self.gridLayout_3 = QtGui.QGridLayout(self.findRoutes_tab)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.txtFindRouteHelp = QtGui.QTextEdit(self.findRoutes_tab)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.txtFindRouteHelp.setFont(font)
        self.txtFindRouteHelp.setReadOnly(True)
        self.txtFindRouteHelp.setObjectName(_fromUtf8("txtFindRouteHelp"))
        self.gridLayout_3.addWidget(self.txtFindRouteHelp, 0, 0, 1, 1)
        self.tbwRoad.addTab(self.findRoutes_tab, _fromUtf8(""))
        self.getDirections_tab = QtGui.QWidget()
        self.getDirections_tab.setObjectName(_fromUtf8("getDirections_tab"))
        self.gridLayout_4 = QtGui.QGridLayout(self.getDirections_tab)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.txtDirectionsHelp = QtGui.QTextEdit(self.getDirections_tab)
        self.txtDirectionsHelp.setReadOnly(True)
        self.txtDirectionsHelp.setObjectName(_fromUtf8("txtDirectionsHelp"))
        self.gridLayout_4.addWidget(self.txtDirectionsHelp, 0, 0, 1, 1)
        self.tbwRoad.addTab(self.getDirections_tab, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.txtDirectionsHelp_2 = QtGui.QTextEdit(self.tab)
        self.txtDirectionsHelp_2.setGeometry(QtCore.QRect(10, 10, 643, 290))
        self.txtDirectionsHelp_2.setReadOnly(True)
        self.txtDirectionsHelp_2.setObjectName(_fromUtf8("txtDirectionsHelp_2"))
        self.tbwRoad.addTab(self.tab, _fromUtf8(""))
        self.about_tab = QtGui.QWidget()
        self.about_tab.setObjectName(_fromUtf8("about_tab"))
        self.gridLayout = QtGui.QGridLayout(self.about_tab)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.about_text = QtGui.QTextEdit(self.about_tab)
        self.about_text.setReadOnly(True)
        self.about_text.setObjectName(_fromUtf8("about_text"))
        self.gridLayout.addWidget(self.about_text, 0, 0, 1, 1)
        self.tbwRoad.addTab(self.about_tab, _fromUtf8(""))
        self.label_11 = QtGui.QLabel(helpDialog)
        self.label_11.setGeometry(QtCore.QRect(20, 360, 211, 111))
        self.label_11.setStyleSheet(_fromUtf8("image: url(:/plugins/floogin/a.png);"))
        self.label_11.setText(_fromUtf8(""))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.btnCloseHelp = QtGui.QPushButton(helpDialog)
        self.btnCloseHelp.setGeometry(QtCore.QRect(570, 426, 98, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.btnCloseHelp.setFont(font)
        self.btnCloseHelp.setObjectName(_fromUtf8("btnCloseHelp"))

        self.retranslateUi(helpDialog)
        self.tbwRoad.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(helpDialog)

    def retranslateUi(self, helpDialog):
        helpDialog.setWindowTitle(_translate("helpDialog", "Help FLOOgin", None))
        self.getting_started_text.setHtml(_translate("helpDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-weight:600; color:#0000ff;\">First things first</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Cantarell\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\';\">These are the first few steps you need to follow in order to use Alternative Route Finder:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Cantarell\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 1</span> : Load the <span style=\" color:#0000ff;\">flood-hazard layer</span> and <span style=\" color:#0000ff;\">road-network layer</span> </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 2</span> : Check whether a file with <span style=\" color:#ff0000;\">.keywords</span> extension, is available in each layer bundle </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 3</span> : If (.keywords files) available, press on <span style=\" color:#0000ff;\">Generate map for process</span> button to generate a <span style=\" color:#0000ff;\">flood-safe</span> layer</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 4</span> : If (.keywords files) <span style=\" color:#ff0000;\">not</span> available, select the <span style=\" color:#0000ff;\">flood-hazard layer</span> and <span style=\" color:#0000ff;\">road-network layer</span> from the drop downs and provide a name for the output shapefile</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 5</span> : <span style=\" color:#ff0000;\">(If followed step 4)</span> press on <span style=\" color:#0000ff;\">Generate map</span> button to generate a <span style=\" color:#0000ff;\">flood-safe</span> layer</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Step 6</span> : The generated <span style=\" color:#0000ff;\">flood-safe</span> layer will be automatically loaded to the TOC and will be saved in the same directory where the other loaded maps are saved </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">    </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0000ff;\">At a Glance</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600; color:#0000ff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\';\">Follow these instructions to view details of a selected road</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Cantarell\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-weight:600;\">1</span><span style=\" font-family:\'Cantarell\';\">. Select road layer from </span><span style=\" font-family:\'Cantarell\'; color:#0000ff;\">Select Road layer</span><span style=\" font-family:\'Cantarell\';\"> drop down</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Cantarell\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-weight:600;\">2</span><span style=\" font-family:\'Cantarell\';\">. Select a road from </span><span style=\" font-family:\'Cantarell\'; color:#0000ff;\">Select a Road to view details</span><span style=\" font-family:\'Cantarell\';\"> drop down</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Cantarell\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-weight:600;\">3</span><span style=\" font-family:\'Cantarell\';\">. Click on </span><span style=\" font-family:\'Cantarell\'; color:#0000ff;\">OK</span><span style=\" font-family:\'Cantarell\';\"> button, to view details of selected road</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600; color:#0000ff;\"><br /></p></body></html>", None))
        self.tbwRoad.setTabText(self.tbwRoad.indexOf(self.getting_started_tab), _translate("helpDialog", "Getting Started", None))
        self.txtFindRouteHelp.setHtml(_translate("helpDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">Follow these instructions in order to Find the best possible alternative route between two selected locations</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; font-size:11pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">1</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Select a </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#ff0000;\">Start</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> location on road layer</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">2</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Select </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#ff0000;\">Stop</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> location</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt;\">    </span><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">2.1</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> Select a </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Stop</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> location on road layer</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt;\">    </span><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">2.2</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> Or select a predefined </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Hospital</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> / </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">IDP camp</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt;\">        </span><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">2.2.1</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> Select Hospital / IDP camp layer from </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Select layer </span><span style=\" font-family:\'Sans\'; font-size:11pt;\">drop down</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt;\">        </span><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">2.2.2</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> Select Hospital / IDP camp name from </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Select Hospital</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> / </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Select IDP Camp</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> drop down</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">3</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Selected location names will be shown in each </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Description</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> box</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-size:11pt; font-weight:600;\">4</span><span style=\" font-family:\'Sans\'; font-size:11pt;\">. Click on </span><span style=\" font-family:\'Sans\'; font-size:11pt; color:#0000ff;\">Find Route</span><span style=\" font-family:\'Sans\'; font-size:11pt;\"> button to find the best possible (Shortest) alternative             route available</span></p></body></html>", None))
        self.tbwRoad.setTabText(self.tbwRoad.indexOf(self.findRoutes_tab), _translate("helpDialog", "Find Route", None))
        self.txtDirectionsHelp.setHtml(_translate("helpDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Follow these instructions in order to get the directions and time to travel between two selected locations</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">1</span><span style=\" font-family:\'Sans\';\">. Founded path is shown in </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Path found</span><span style=\" font-family:\'Sans\';\"> box</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">2</span><span style=\" font-family:\'Sans\';\">. Length of the founded path is shown in</span><span style=\" font-family:\'Sans\'; color:#0000ff;\"> Length</span><span style=\" font-family:\'Sans\';\"> box</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\';\">    </span><span style=\" font-family:\'Sans\'; font-weight:600;\">2.1</span><span style=\" font-family:\'Sans\';\"> Length metric can be changed in to </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">km</span><span style=\" font-family:\'Sans\';\"> (kilometers), </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">mile</span><span style=\" font-family:\'Sans\';\"> or </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">m</span><span style=\" font-family:\'Sans\';\"> (meters)</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">3</span><span style=\" font-family:\'Sans\';\">. Select mode of transport - </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">By Car</span><span style=\" font-family:\'Sans\';\"> or </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Walking</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; color:#0000ff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">4</span><span style=\" font-family:\'Sans\';\">. Once selected, the default speed of travel ( can change ) for each selection is selected in </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Speed of travel</span><span style=\" font-family:\'Sans\';\"> drop down</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\';\">(eg : average human walking speed is about 5.0 kilometres per hour (km/h), or about 3.1 miles per hour (mph))</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\';\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">5</span><span style=\" font-family:\'Sans\';\">. Miles per hour according to the </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">km / h</span><span style=\" font-family:\'Sans\';\"> selected, is shown in </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">mph</span><span style=\" font-family:\'Sans\';\"> box</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">6</span><span style=\" font-family:\'Sans\';\">. Number of hours and minutes required for the travel is shown in </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Average time to travel</span><span style=\" font-family:\'Sans\';\"> boxes</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">7</span><span style=\" font-family:\'Sans\';\">. Click on </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Get directions</span><span style=\" font-family:\'Sans\';\"> button to view the step by step directions, to reach the destination</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">8</span><span style=\" font-family:\'Sans\';\">. Click on </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Show on Map</span><span style=\" font-family:\'Sans\';\"> button and move the mouse through the path to view the names of the roads </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\';\"> </span></p></body></html>", None))
        self.tbwRoad.setTabText(self.tbwRoad.indexOf(self.getDirections_tab), _translate("helpDialog", "Get Directions", None))
        self.txtDirectionsHelp_2.setHtml(_translate("helpDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Follow these instructions in order to find the details of roads which have access issues</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#aa0000;\">Basic</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">1</span><span style=\" font-family:\'Sans\';\">. Make sure you have generated the </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">flood-safe</span><span style=\" font-family:\'Sans\';\"> layer by following instructions specified in </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Getting Started</span><span style=\" font-family:\'Sans\';\"> page</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">2</span><span style=\" font-family:\'Sans\';\">. Click on </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Blocked Roads Details</span><span style=\" font-family:\'Sans\';\"> button to view details about the roads which have been blocked due to flood</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; color:#aa0000;\">Advanced</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; color:#aa0000;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">1</span><span style=\" font-family:\'Sans\';\">. Make sure you have identified the </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Blocked Roads</span><span style=\" font-family:\'Sans\';\">, by following </span><span style=\" font-family:\'Sans\'; color:#aa0000;\">Basic</span><span style=\" font-family:\'Sans\';\"> steps above</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">2</span>. Load the <span style=\" color:#0000ff;\">Administrative Divisions Layer</span> to QGIS</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">3</span>. Select the <span style=\" color:#0000ff;\">Administrative Divisions Layer</span> from the combo box <span style=\" color:#0000ff;\">Select Administrative Divisions Layer</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">4</span><span style=\" font-family:\'Sans\';\">. Click on button </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Generate map for process</span><span style=\" font-family:\'Sans\';\"> to generate the layer which is needed for the rest of the process</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">5</span><span style=\" font-family:\'Sans\';\">. Select the radio button - </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">All</span><span style=\" font-family:\'Sans\';\"> OR </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Specific</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; color:#0000ff;\">All</span><span style=\" font-family:\'Sans\';\"> - View details of blocked roads of all Provinces, Districts, Divisional Secretariats and Grama Niladhari Administration Divisions</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; color:#0000ff;\">Specific</span><span style=\" font-family:\'Sans\';\"> - View details of blocked roads for a specific Province, District, Divisional Secretariat and Grama Niladhari Administration Division </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">6</span><span style=\" font-family:\'Sans\';\">. </span><span style=\" font-family:\'Sans\'; font-weight:600;\">If selected</span><span style=\" font-family:\'Sans\';\">, </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; color:#0000ff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">6.1</span><span style=\" font-family:\'Sans\';\"> radio button </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">All,</span><span style=\" font-family:\'Sans\';\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">6.1.1</span><span style=\" font-family:\'Sans\';\"> Select an Administration Division that you want the results to be sorted </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">6.1.2</span><span style=\" font-family:\'Sans\';\"> Select radio button </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">ASC</span><span style=\" font-family:\'Sans\';\"> for sort the results in Ascending order or </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">DESC</span><span style=\" font-family:\'Sans\';\"> for sort the results in Descending order</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">6.2</span><span style=\" font-family:\'Sans\';\"> radio button </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Specific,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">6.2.1</span><span style=\" font-family:\'Sans\';\"> Select the Province from combo box </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Select Province</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">6.2.2</span><span style=\" font-family:\'Sans\';\"> Select the District from combo box </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">District</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">6.2.3</span><span style=\" font-family:\'Sans\';\"> Select the Divisional Secretariat from combo box </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">DS</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">6.2.4</span><span style=\" font-family:\'Sans\';\"> Select the Grama Niladhari Administration Division from combo box </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">GND</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Sans\'; color:#0000ff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">7</span><span style=\" font-family:\'Sans\';\">. Click on </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">View Blocked Roads Details</span><span style=\" font-family:\'Sans\';\"> button to view the details of blocked roads for mentioned requirements </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\';\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans\'; font-weight:600;\">8</span><span style=\" font-family:\'Sans\';\">. Click on </span><span style=\" font-family:\'Sans\'; color:#0000ff;\">Generate Report</span><span style=\" font-family:\'Sans\';\"> button to generate a pdf report which includes the generated information</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.tbwRoad.setTabText(self.tbwRoad.indexOf(self.tab), _translate("helpDialog", "Find Blocked Roads", None))
        self.about_text.setHtml(_translate("helpDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#ff0000;\">FLOOgin</span> is a fully automated Free and Open Source tool or a plugin for QGIS (Quantum Geographic Information System) software, which helps to response immediately when a flooding disaster strikes and aims to produce a realistic natural hazard impact scenarios for better planning, preparedness and response activities using hazard and exposure geographic data. </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> consists with impact functions which provides information about</span>, Health Risks (Epidemic diseases), Medicinal resources (Number of medical practitioners, Drugs, Vaccinations, Ambulances), Hospitals with capacities (number of beds) </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> will identify the </span>villages, resource centres (IDP camps), nearby hospitals which has limited road accessibility due to flood.</p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> will identify the </span>best possible<span style=\" font-weight:600;\"> </span>alternative route available to reach affected locations identified above. </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> will help to </span>allocate flood victims to identified resource centres based on available facilities and capacities </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> will</span> generate reports and related maps to above mentioned tools. </p>\n"
"<p align=\"justify\" style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">FLOOgin</span><span style=\" font-weight:600;\"> will</span> allow user to share the reports generated via user\'s email service provider. </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.tbwRoad.setTabText(self.tbwRoad.indexOf(self.about_tab), _translate("helpDialog", "About FLOOgin", None))
        self.btnCloseHelp.setText(_translate("helpDialog", "Close", None))

import resources_rc
