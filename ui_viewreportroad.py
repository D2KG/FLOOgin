# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_viewreportroad.ui'
#
# Created: Mon Jul 21 23:06:28 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
class viewReportRoadDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
	self.uiViewR = Ui_viewReportRoad()
        self.uiViewR.setupUi(self)
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

class Ui_viewReportRoad(object):
    def setupUi(self, viewReportRoad):
        viewReportRoad.setObjectName(_fromUtf8("viewReportRoad"))
        viewReportRoad.resize(604, 216)
        self.label = QtGui.QLabel(viewReportRoad)
        self.label.setGeometry(QtCore.QRect(30, 20, 421, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(viewReportRoad)
        self.label_2.setGeometry(QtCore.QRect(30, 50, 341, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(viewReportRoad)
        self.label_3.setGeometry(QtCore.QRect(30, 90, 141, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.lblViewRepRoad = QtGui.QLabel(viewReportRoad)
        self.lblViewRepRoad.setGeometry(QtCore.QRect(30, 140, 261, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lblViewRepRoad.setFont(font)
        self.lblViewRepRoad.setObjectName(_fromUtf8("lblViewRepRoad"))
        self.btnOKReport = QtGui.QPushButton(viewReportRoad)
        self.btnOKReport.setGeometry(QtCore.QRect(30, 170, 98, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.btnOKReport.setFont(font)
        self.btnOKReport.setObjectName(_fromUtf8("btnOKReport"))
        self.btnNotNowReport = QtGui.QPushButton(viewReportRoad)
        self.btnNotNowReport.setGeometry(QtCore.QRect(150, 170, 98, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.btnNotNowReport.setFont(font)
        self.btnNotNowReport.setObjectName(_fromUtf8("btnNotNowReport"))
        self.btnSaveReportRoad = QtGui.QPushButton(viewReportRoad)
        self.btnSaveReportRoad.setGeometry(QtCore.QRect(490, 90, 98, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.btnSaveReportRoad.setFont(font)
        self.btnSaveReportRoad.setObjectName(_fromUtf8("btnSaveReportRoad"))
        self.txtReportNameRoad = QtGui.QLineEdit(viewReportRoad)
        self.txtReportNameRoad.setGeometry(QtCore.QRect(180, 90, 291, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.txtReportNameRoad.setFont(font)
        self.txtReportNameRoad.setObjectName(_fromUtf8("txtReportNameRoad"))
        self.label_4 = QtGui.QLabel(viewReportRoad)
        self.label_4.setGeometry(QtCore.QRect(550, 20, 31, 31))
        self.label_4.setStyleSheet(_fromUtf8("image: url(:/plugins/floogin/rep.png);"))
        self.label_4.setText(_fromUtf8(""))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.btnEmailRep = QtGui.QPushButton(viewReportRoad)
        self.btnEmailRep.setGeometry(QtCore.QRect(490, 150, 98, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.btnEmailRep.setFont(font)
        self.btnEmailRep.setStyleSheet(_fromUtf8("background-color: rgb(85, 170, 255);\n"
"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0.654028 rgba(17, 88, 146, 255), stop:1 rgba(255, 255, 255, 255));\n"
"color: rgb(255, 255, 255);"))
        self.btnEmailRep.setObjectName(_fromUtf8("btnEmailRep"))

        self.retranslateUi(viewReportRoad)
        QtCore.QMetaObject.connectSlotsByName(viewReportRoad)

    def retranslateUi(self, viewReportRoad):
        viewReportRoad.setWindowTitle(_translate("viewReportRoad", "Alternative Route Finder - Report Generation", None))
        self.label.setText(_translate("viewReportRoad", "Report generated successfully", None))
        self.label_2.setText(_translate("viewReportRoad", "Location :  /home directory", None))
        self.label_3.setText(_translate("viewReportRoad", "Name of report ", None))
        self.lblViewRepRoad.setText(_translate("viewReportRoad", "Report Saved . View Report ?", None))
        self.btnOKReport.setText(_translate("viewReportRoad", "OK", None))
        self.btnNotNowReport.setText(_translate("viewReportRoad", "Not Now", None))
        self.btnSaveReportRoad.setText(_translate("viewReportRoad", "Save", None))
        self.btnEmailRep.setText(_translate("viewReportRoad", "E mail to", None))

import resources_rc
