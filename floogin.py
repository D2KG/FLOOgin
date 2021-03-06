# -*- coding: utf-8 -*-
"""
/***************************************************************************
 floogin
                                 A QGIS plugin
 Flood Disaster Management
                              -------------------
        begin                : 2014-05-03
        copyright            : (C) 2014 by FLOOgin group
        email                : kasun.ramanayake@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
#from floogindialog import flooginDialog
from ui_floogin import flooginDialog
#import os.path
from qgis.gui import *
from qgis.networkanalysis import *
#from astar_grid import AStarGrid, AStarGridNode
#from itertools import product
from astar import AStar#, AStarNode
from dijkstra import Dijk
import networkx as nx
#import nx_spatial as nx
from astarAlgorithm import astarAlgo
#astar with obstacles
#from astar_gridObs import AStarGridObs, AStarGridNodeObs
from itertools import product
#from astarObs import AStarObs, AStarNodeObs
#for keywords
#from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from exceptions import (
    HashNotFoundError,
    KeywordNotFoundError,
    KeywordDbError,
    InvalidParameterError,
    #NoKeywordsFoundError,
    UnsupportedProviderError)
import sqlite3 as sqlite
from sqlite3 import OperationalError
# Standard modules
import os
import unicodedata
import logging
import processing
# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignature

from third_party.odict import OrderedDict

from safe_qgis.safe_interface import InaSAFEError, get_version
#from safe_qgis.ui.keywords_dialog_base import Ui_KeywordsDialogBase
from safe_qgis.utilities.defaults import breakdown_defaults
from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.utilities.help import show_context_help
from safe_qgis.utilities.utilities import (
    get_error_message,
    is_polygon_layer,
    layer_attribute_names)
from safe_qgis.exceptions import (
    InvalidParameterError,
    HashNotFoundError)
    #NoKeywordsFoundError)
import math
#from IPython.display import HTML
import string
import sys
#Google Text To Speech
#from GoogleTTS import GoogleTTSS
import subprocess
#pdf report
from reportlab.platypus import Paragraph, SimpleDocTemplate,Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, mm, inch, pica
from reportlab.platypus import Image, Table, TableStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics 
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.samples.excelcolors import * 
from reportlab.lib.colors import HexColor
#from PyPDF2 import PdfFileMerger, PdfFileReader
#from reportlab.pdfgen.canvas import Canvas
#from reportlab.lib.pagesizes import letter
#google maps
#from googlemaps import GoogleMaps
from HTMLParser import HTMLParser
#help dialog
from ui_helpdialog import helpDialogDialog
#help dialog IDP
from ui_helpdialogidp import helpDialogIDPDialog
#view report road
from ui_viewreportroad import viewReportRoadDialog
#email report road
from ui_emailreportroad import emailReportRoadDialog
#from Tkinter import *
#from tkFileDialog import askopenfilename
import webbrowser
#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive
#import fiona
#from shapely.geometry import Point
## send email
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import email
import email.mime.application
#pdf page no
from numberedcan import NumberedCanvas
import datetime
#for sort by blocked roads
from osgeo import ogr
#show how result - road
from resultDialogR_dialog import resultDialogRDialog
#move files
import shutil, errno
#** dish_ Help Dialog**#
from ui_helpdialoghosp import HelpDialogHospDialog

## Giv
from qgis.analysis import *
from pylab import *
import gtk.gdk


class floogin:

    def __init__(self, iface, layer=None):
        # Save reference to the QGIS interface
        self.iface = iface
	# a reference to our map canvas
    	self.canvas = self.iface.mapCanvas() #CHANGE
    	# this QGIS tool emits as QgsPoint after each click on the map canvas
    	self.clickTool = QgsMapToolEmitPoint(self.canvas)
	#self.curMove = QgsMapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'floogin_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = flooginDialog()
	#help dialog
	self.dlgHelp = helpDialogDialog()
	#view report road
	self.dlgViewR = viewReportRoadDialog()
	#email report road
	self.dlgEmailR = emailReportRoadDialog()
    	# create a list to hold our selected feature ids
    	self.selectList = []
    	# current layer ref (set in handleLayerChange)
    	self.cLayer = None
    	# current layer dataProvider ref (set in handleLayerChange)
    	self.provider = None

	fid=0
	x1=0
	y1=0
	x2=0
	y2=0
	source = ''
	no=0
	global n
	n = 0
	global now
	now = 2
	#global stopNow
	stopNow = 0
	resultCon = False
	global okNow
	okNow = 1
	stopPlace = 0
	#global rH
	#rH = 0
	#global rI
	#rI = 0
	global host
	global port
	host = ''
	port = 0 
	global All
	All = "no"
	global asc
 	asc = "yes"
	self.dlg.ui.btnShowDirOnMap.setVisible(False)
	self.dlg.ui.lblShowDirOnMap.setVisible(False)
	self.dlg.ui.btnStopShowLoc.setVisible(False)
	self.dlg.ui.lblOsmIdGlance.setVisible(False)
	self.dlg.ui.lblClassGlance.setVisible(False)
	self.dlg.ui.lblTypeGlance.setVisible(False)
	self.dlg.ui.btnDirectionstxt.setVisible(False)
	self.dlg.ui.btnDirectionsImage.setVisible(False)
	self.dlg.ui.btnDirectionsPDF.setVisible(False)
	self.dlg.ui.btnDirectionsAudio.setVisible(False)
	self.dlg.ui.lblGenerateDirecFiles.setVisible(False)
	self.dlg.ui.btnshowDetailsHos.setVisible(False)
	self.dlg.ui.btnshowDetailsIDP.setVisible(False)	

	#self.googletts = GoogleTTSS()
	self.astar = AStar()
	self.dijk = Dijk()
	self.astarnetx = astarAlgo()

	##Keywords*****************************

	layer_path_haz = ''
	layer_path_rd = ''
	layer=None
	floodLayer = ''
	global rdPath
	rdPath = ''
	global fdPath
	fdPath = ''
	global repID
	repID = 0
	global direcFilesID
	direcFilesID = 0

	try:
    		_fromUtf8 = QtCore.QString.fromUtf8
	except AttributeError:
    		def _fromUtf8(s):
        		return s

	self.dlgResD = resultDialogRDialog()

        ##if layer is None:
            ##self.layer = iface.activeLayer()
        ##else:
            ##self.layer = layer

        self.keyword_io = KeywordIO()

        # note the keys should remain untranslated as we need to write
        # english to the keywords file. The keys will be written as user data
        # in the combo entries.
        # .. seealso:: http://www.voidspace.org.uk/python/odict.html
        self.standard_exposure_list = OrderedDict(
            [('population', 'population'),
             ('structure', 'structure'),
             ('road', 'road'),
             ('Not Set', 'Not Set')])
        self.standard_hazard_list = OrderedDict(
            [('flood [m]', 'flood [m]'),
             ('flood [wet/dry]', 'flood [wet/dry]'),
             ('flood [feet]', 'flood [feet]'),
             ('Not Set', 'Not Set')])

        #self.lstKeywords.itemClicked.connect(self.edit_key_value_pair)

        # Set up help dialog showing logic.
        ##help_button = self.buttonBox.button(QtGui.QDialogButtonBox.Help)
        ##help_button.clicked.connect(self.show_help)

        # set some initial ui state:
        self.defaults = breakdown_defaults()
        #self.pbnAdvanced.setChecked(False)
        #self.radPredefined.setChecked(True)
        #self.dsbFemaleRatioDefault.blockSignals(True)
        #self.dsbFemaleRatioDefault.setValue(self.defaults['FEMALE_RATIO'])
        #self.dsbFemaleRatioDefault.blockSignals(False)
        #self.dsbYouthRatioDefault.blockSignals(True)
        #self.dsbYouthRatioDefault.setValue(self.defaults['YOUTH_RATIO'])
        #self.dsbYouthRatioDefault.blockSignals(False)
        #self.dsbAdultRatioDefault.blockSignals(True)
        #self.dsbAdultRatioDefault.setValue(self.defaults['ADULT_RATIO'])
        #self.dsbAdultRatioDefault.blockSignals(False)
        #self.dsbElderlyRatioDefault.blockSignals(True)
        #self.dsbElderlyRatioDefault.setValue(self.defaults['ELDERLY_RATIO'])
        #self.dsbElderlyRatioDefault.blockSignals(False)

        #myButton = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        #myButton.setEnabled(False)
        if layer is None:
            self.layer = self.iface.activeLayer()
        else:
            self.layer = layer

	allLayersLoaded = self.canvas.layers()
 	for SelLayer in allLayersLoaded:	
		self.dlg.ui.cboRoadLayer.addItem(SelLayer.name())
                self.dlg.ui.cboFloodLayer.addItem(SelLayer.name())
		self.dlg.ui.cmbHospitalLayerR.addItem(SelLayer.name())
		self.dlg.ui.cmbIDPCampLayerR.addItem(SelLayer.name())		
		self.dlg.ui.cmbAdminiLayer.addItem(SelLayer.name())
		self.dlg.ui.cmbLayerLabelling.addItem(SelLayer.name())		
		#dil
		self.dlg.ui.cboIDPLayer.addItem(SelLayer.name())
                self.dlg.ui.cboFloodLayerIDP.addItem(SelLayer.name())
		self.dlg.ui.cmbSelectPopLayer.addItem(SelLayer.name())
		#dil
	self.atGlnaceRoadsReset()
	global IDPSafePathManu
	IDPSafePathManu = ''
	#self.cursor = QCursor()
	# lable for mouse cursor movements
	self.labelPos = QtGui.QLabel(self.canvas)
	font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(100)
        self.labelPos.setFont(font)
	self.labelPos.setObjectName(_fromUtf8("labelPos"))
	self.labelPos.setStyleSheet(_fromUtf8("color: rgb(170, 0, 0);"))
	self.labelDirPlc = QtGui.QLabel(self.canvas)
	colRd = '<font color="red">'
	colRds = '</font>'
	self.dlg.ui.txtFirstSteps.clear()
	self.dlg.ui.txtFirstSteps.setText(colRd + "<b>Please follow these steps</b>" + colRds + '\n' + "<b>(Press on down arrow to start)</b>")
	self.dlg.ui.lblWarnRoad.setVisible(False)
	self.dlg.ui.lblNoIDPReach.setVisible(False)
	self.dlg.ui.lblNoHospReach.setVisible(False)
	self.dlg.ui.lblWait.setVisible(False)


        #group brCat radio buttons
	self.groupMain = QtGui.QButtonGroup()	
	self.groupMain.addButton(self.dlg.ui.rdAllBlocked)
	self.groupMain.addButton(self.dlg.ui.rdCatBlocked)
	self.groupSub = QtGui.QButtonGroup()	
	self.groupSub.addButton(self.dlg.ui.rdAscSort)
	self.groupSub.addButton(self.dlg.ui.rdDescSort)
	#blocked roads cat
	self.dlg.ui.lblProvince.setVisible(False)
	self.dlg.ui.cmbProvince.setVisible(False)
	self.dlg.ui.lblDistrict.setVisible(False)
	self.dlg.ui.cmbDistrict.setVisible(False)
	self.dlg.ui.lblDS.setVisible(False)
	self.dlg.ui.cmbDS.setVisible(False)
	self.dlg.ui.lblGND.setVisible(False)
	self.dlg.ui.cmbGND.setVisible(False)
	self.dlg.ui.lblDSDesc.setVisible(False)
	self.dlg.ui.lblGNDDesc.setVisible(False)
	self.dlg.ui.cmbProvince.addItem("Select Province")
	self.dlg.ui.cmbDistrict.addItem("Select District")
	self.dlg.ui.cmbDS.addItem("Select DS")
	self.dlg.ui.cmbGND.addItem("Select GND")
	self.dlg.ui.btnProvinceOk.setVisible(False)
 	self.dlg.ui.btnDistOk.setVisible(False)
	self.dlg.ui.btnDSOk.setVisible(False)
	self.dlg.ui.btnGNDOk.setVisible(False)
	#invisible rdAll fields
	self.dlg.ui.lblSortByR.setVisible(False)
	self.dlg.ui.cmbSortByAdmin.setVisible(False)
	self.dlg.ui.rdAscSort.setVisible(False)
	self.dlg.ui.lblAsc.setVisible(False)
	self.dlg.ui.rdDescSort.setVisible(False)
	self.dlg.ui.lblDesc.setVisible(False)
	global bRoadsCatForReport
	global bRoadsCatSpeciForReport
	bRoadsCatForReport = []
	bRoadsCatSpeciForReport = []
	global stopPlace
	stopPlace = 0


	#self.numCanvas = NumberedCanvas()
	#self.labelPos.setVisible(True)	

	#self.labelPos.setVisible(True)
	
	#self.pointCursor()

        ##if self.layer:
            ##self.load_state_from_keywords()
	##self.keywords_from_layers()

        # add a reload from keywords button
        #reload_button = self.buttonBox.addButton(
            #self.tr('Reload'), QtGui.QDialogButtonBox.ActionRole)
        #reload_button.clicked.connect(self.load_state_from_keywords)
        #self.grpAdvanced.setVisible(False)
        #self.resize_dialog()
	#*****************************dil
	colRd = '<font color="red">'
	colRds = '</font>'
	self.dlg.ui.txtFirstStepsIDP.clear()
	self.dlg.ui.txtFirstStepsIDP.setText(colRd + "<b>Please follow these steps</b>" + colRds + '\n' + "<b>(Press on down arrow to start)</b>")
	layer_path_build = ''
	global rangeIDP
	rangeIDP = 0
	global nIDP
	nIDP = 0
	global nowIDP
	nowIDP = 2
	#help dialog IDP
	self.dlgHelpIDP = helpDialogIDPDialog()
	global fdPathIDP
	fdPathIDP = ''
	global IDPSafePath
	IDPSafePath = ''
	#***************************dil


        #***********intialize variables_dish*****************************#
	colRdN = '<font color="red">'
	colRdsN = '</font>'
	self.dlg.ui.txtStepsN.clear()
	self.dlg.ui.txtStepsN.setText(colRdN + "<b>Please follow these steps</b>" + colRdsN + '\n' + "<b>(Press on down arrow to start)</b>")
	self.dlgHelpHos = HelpDialogHospDialog()      
        global nHos
        nHos = 0
        global nowHos
        nowHos = 2         
        NonHosCount = 0 
        ListOfNonAffectedHos = []
	#HospReport = []
	#DocReport = []
        #HospReport = []
    	global mHos1
    	mHos1 = []
    	global mHos2
    	mHos2 = []

	
        
        layer_HospitalsNonAffected = ''
        layer_path_hazN = ''
        layer_path_rdN = ''
        layer=''
        floodLayerN = ''
        
	allLayersLoadedN = self.canvas.layers()
 	for SelLayerN in allLayersLoadedN:	
		self.dlg.ui.cmbSelectBuildingLayerN.addItem(SelLayerN.name())
                self.dlg.ui.cmbSelectFloodLayerN.addItem(SelLayerN.name())
		self.dlg.ui.cmbAdminLayerN.addItem(SelLayerN.name())
		#self.dlg.ui.cmbAdminLayerGN.addItem(SelLayerN.name())
		

	#***********End_intialize variables_dish*****************************#


	############## Givanthika
	 ################# Giv ################################
	self.dlg.ui.lblNotSufficient.setVisible(False)
	self.dlg.ui.lblSufficient.setVisible(False)

	global storyWelRep
	storyWelRep = []

	global detailsWell
	detailsWell = []

	global drugNameList
	drugNameList=[]
	global drugPriceList
	drugPriceList=[]

	global drugPrice
	drugPrice=[]

	global doseChildrenList
	doseChildrenList=[]
	global doseAdultList
	doseAdultList=[]
	global drugTotN
	drugTotN = []

	global drugPrice
	drugPrice =[]

	global drugNameListG
	drugNameListG=[]
	global drugPriceListG
	drugPriceListG=[]
	global drugPriceG
	drugPriceG=[]
	global doseChildrenListG
	doseChildrenListG=[]
	global doseAdultListG
	doseAdultListG=[]

	global drugNameLista
	drugNameLista=[]
	global drugPriceLista
	drugPriceLista=[]
	global drugPricea
	drugPricea=[]
	global doseChildrenLista
	doseChildrenLista=[]
	global doseAdultLista
	doseAdultLista=[]

	global drugNameListb
	drugNameListb=[]
	global drugPriceListb
	drugPriceListb=[]
	global drugPriceb
	drugPriceb=[]
	global doseChildrenListb
	doseChildrenListb=[]
	global doseAdultListb
	doseAdultListb=[]

	self.dlg.ui.txtTotQtyCount.setVisible(False)

	global gWellLoc
	global gWellLocAll
	

	global stepzz
	stepzz = []

	global drugNameListc
	drugNameListc=[]
	global drugPriceListc
	drugPriceListc=[]
	global drugPricec
	drugPricec=[]
	global doseChildrenListc
	doseChildrenListc=[]
	global doseAdultListc
	doseAdultListc=[]

	global drugNameListd
	drugNameListd=[]
	global drugPriceListd
	drugPriceListd=[]
	global drugPriced
	drugPriced=[]
	global drugPriceNew
	drugPriceNew = []
	global doseChildrenListd
	doseChildrenListd=[]
	global doseAdultListd
	doseAdultListd=[]

	global drug1Report
	drug1Report = []

	global storyBudget
	storyBudget = []
	global detailsBudget
	detailsBudget = [] #drugReport
	global drugReport
	drugReport = []

	global storyBudget2
	storyBudget2 = []
	global detailsBudget2
	detailsBudget2 = [] #drugReport
	global drugReport2
	drugReport2 = []

	global storyBudget3
	storyBudget3 = []
	global detailsBudget3
	detailsBudget3 = [] #drugReport
	global drugReport3
	drugReport3 = []

	global storyBudget4
	storyBudget4 = []
	global detailsBudget4
	detailsBudget4 = [] #drugReport
	global drugReport4
	drugReport4 = []

	global storyBudget5
	storyBudget5 = []
	global detailsBudget5
	detailsBudget5 = [] #drugReport
	global drugReport5
	drugReport5 = []

	global drugChildQty
	drugChildQty = []

	global drugAdultQty
	drugAdultQty = []

	global storyWelRep
	storyWelRep = []
	global detailsWell
	detailsWell = [] #drugReport
	global wellReport
	wellReport = []

	global storyWSRep
	storyWSRep = []
	global detailsWS
	detailsWS = [] #drugReport
	global wsReport
	wsReport = []

	global height
	height = []
	global xAxis
	xAxis = []
	global bar

	global frac
	frac = []
	global labels
	labels = []
	global explode
	explode = []

	self.dlg.ui.txtDoseC.setVisible(False)
	self.dlg.ui.txtDoseA.setVisible(False)
	
	self.dlg.ui.lblPlaceWell.setVisible(False)
	self.dlg.ui.lblWellId.setVisible(False)
	self.dlg.ui.lblOwnnerWell.setVisible(False)
	self.dlg.ui.lbldepthWell.setVisible(False)


	self.dlg.ui.lblDrugName.setVisible(False)
	self.dlg.ui.lblChildDose.setVisible(False)
	self.dlg.ui.lblAdultDose.setVisible(False)
	self.dlg.ui.lblUnitPrice.setVisible(False)
	self.dlg.ui.lblTotPrice.setVisible(False)
	self.dlg.ui.lblTotQty.setVisible(False)

	self.dlg.ui.lblmg1_9.setVisible(False)
	self.dlg.ui.lblPack1_7.setVisible(False)
	self.dlg.ui.lblmg1_10.setVisible(False)


	self.dlg.ui.txtAdQ1.setVisible(False)
	self.dlg.ui.txtAdQ2.setVisible(False)
	self.dlg.ui.txtAdQ3.setVisible(False)
	self.dlg.ui.txtAdQ4.setVisible(False)
	self.dlg.ui.txtChQ1.setVisible(False)
	self.dlg.ui.txtChQ2.setVisible(False)
	self.dlg.ui.txtChQ3.setVisible(False)
	self.dlg.ui.txtChQ4.setVisible(False)

	self.dlg.ui.btnGenerateMapWell.setVisible(False)
	self.dlg.ui.btnGenerateMapSources.setVisible(False)
	self.dlg.ui.btnGenerateMapDrug.setVisible(False)

	self.dlg.ui.txtdrugMan.setVisible(False)

	self.dlg.ui.lblGNArea_3.setVisible(False)
	self.dlg.ui.lblGNArea_4.setVisible(False)


	self.dlg.ui.lblGNArea_2.setVisible(False)
	self.dlg.ui.lblGNArea.setVisible(False)
	self.dlg.ui.lblProvnStatus.setVisible(False)
	self.dlg.ui.lblGNFemale.setVisible(False)
	self.dlg.ui.lblGNMale.setVisible(False)

	self.dlg.ui.cmbdiarrhea.setVisible(False) 
	self.dlg.ui.cmbhepatis.setVisible(False)
	self.dlg.ui.cmblept.setVisible(False)
	self.dlg.ui.cmbMisl.setVisible(False)
	self.dlg.ui.cmbARI.setVisible(False) 
	self.dlg.ui.lblRs.setVisible(False)

	
	self.dlg.ui.txtDrug2.setText(str())
	self.dlg.ui.txtChildDose2.setText(str(0))
	self.dlg.ui.txtAdultDose2.setText(str(0))
	self.dlg.ui.txtUP2.setText(str(0))
	self.dlg.ui.txtTot2.setText(str(0.0))
	self.dlg.ui.txtTotQty2.setText(str(0.0))

	self.dlg.ui.txtDrug3.setText(str())
	self.dlg.ui.txtChildDose3.setText(str(0))
	self.dlg.ui.txtAdultDose3.setText(str(0))
	self.dlg.ui.txtUP3.setText(str(0))
	self.dlg.ui.txtTot3.setText(str(0.0))
	self.dlg.ui.txtTotQty3.setText(str(0.0))

	self.dlg.ui.txtDrug4.setText(str())
	self.dlg.ui.txtChildDose4.setText(str(0))
	self.dlg.ui.txtAdultDose4.setText(str(0))
	self.dlg.ui.txtUP4.setText(str(0))
	self.dlg.ui.txtTot4.setText(str(0.0))
	self.dlg.ui.txtTotQty4.setText(str(0.0))

	self.dlg.ui.txtDrug1.setVisible(False)
	self.dlg.ui.txtChildDose1.setVisible(False)
	self.dlg.ui.txtAdultDose1.setVisible(False)
	self.dlg.ui.txtUP1.setVisible(False)
	self.dlg.ui.btnAddD1.setVisible(False)
	self.dlg.ui.txtTot1.setVisible(False)
	self.dlg.ui.txtTotQty1.setVisible(False)


	self.dlg.ui.lblNoDys.setVisible(False)
	self.dlg.ui.txtNoOfDays.setVisible(False)
	self.dlg.ui.lblCapSize.setVisible(False)
	self.dlg.ui.cmbDrugSize.setVisible(False)
	self.dlg.ui.lblmg1_9.setVisible(False)
	

	self.dlg.ui.txtDrug2.setVisible(False)
	self.dlg.ui.txtChildDose2.setVisible(False)
	self.dlg.ui.txtAdultDose2.setVisible(False)
	self.dlg.ui.txtUP2.setVisible(False)
	self.dlg.ui.btnAddD2.setVisible(False)
	self.dlg.ui.txtTot2.setVisible(False)
	self.dlg.ui.txtTotQty2.setVisible(False)

	self.dlg.ui.txtDrug3.setVisible(False)
	self.dlg.ui.txtChildDose3.setVisible(False)
	self.dlg.ui.txtAdultDose3.setVisible(False)
	self.dlg.ui.txtUP3.setVisible(False)
	self.dlg.ui.btnAddD3.setVisible(False)
	self.dlg.ui.txtTot3.setVisible(False)
	self.dlg.ui.txtTotQty3.setVisible(False)

	self.dlg.ui.txtDrug4.setVisible(False)
	self.dlg.ui.txtChildDose4.setVisible(False)
	self.dlg.ui.txtAdultDose4.setVisible(False)
	self.dlg.ui.txtUP4.setVisible(False)
	self.dlg.ui.btnAddD4.setVisible(False)
	self.dlg.ui.txtTot4.setVisible(False)
	self.dlg.ui.txtTotQty4.setVisible(False) 

	#self.dlg.ui.label_112.setVisible(False)


	self.dlg.ui.lblmg1.setVisible(False)
	self.dlg.ui.lblmg1_2.setVisible(False)
	self.dlg.ui.lblmg1_3.setVisible(False)
	self.dlg.ui.lblmg1_4.setVisible(False)
	self.dlg.ui.lblmg1_5.setVisible(False)
	self.dlg.ui.lblmg1_6.setVisible(False)
	self.dlg.ui.lblPack1.setVisible(False)
	self.dlg.ui.lblPack1_2.setVisible(False)
	self.dlg.ui.lblPack1_3.setVisible(False)
	self.dlg.ui.lblPack1_4.setVisible(False)
	self.dlg.ui.lblPack1_5.setVisible(False)
	self.dlg.ui.lblPack1_6.setVisible(False) 

	self.dlg.ui.txtTime.setVisible(False)
	self.dlg.ui.txtTime_2.setVisible(False) 
	self.dlg.ui.lblmg1_7.setVisible(False)
	self.dlg.ui.lblmg1_8.setVisible(False) 
	self.dlg.ui.txtAllTota.setVisible(False)

	self.dlg.ui.btnRefreshWell.setVisible(False)
	self.dlg.ui.btnResetWell.setVisible(False) 

	self.dlg.ui.btnRefreshWell_4.setVisible(False)
	self.dlg.ui.btnResetWell_4.setVisible(False) 

	self.dlg.ui.btnHelpIDPa_2.setVisible(False)
	self.dlg.ui.btnHelpSources.setVisible(False)

	self.dlg.ui.lblGNArea.setVisible(False)
	self.dlg.ui.lblProvnStatus.setVisible(False)
	self.dlg.ui.lblGNFemale.setVisible(False)
	self.dlg.ui.lblGNMale.setVisible(False)

	
	self.dlg.ui.lblBudView.setVisible(False)
	

	self.dlg.ui.label_100.setVisible(False)
	#self.dlg.ui.label_106.setVisible(False)
#
	

	self.dlg.ui.chkOverEighteenAff_3.setVisible(False)
	self.dlg.ui.chkUnderEighteenAff_3.setVisible(False)

	
	self.dlg.ui.lblMeaslImmun.setVisible(False)
	self.dlg.ui.lblMeaslImmunNormal.setVisible(False)
	
	self.dlg.ui.btnClearSources.setVisible(False)
	self.dlg.ui.btnClearWella.setVisible(False)
	self.dlg.ui.btnRefreshDrug.setVisible(False)
	self.dlg.ui.btnResetDrug.setVisible(False)

	self.dlg.ui.lblLepHos.setVisible(False) 
	self.dlg.ui.lblLepHos_2.setVisible(False)

	self.dlg.ui.txtOutBreak_4.setVisible(False)
	self.dlg.ui.txtOutBreak_3.setVisible(False)
	self.dlg.ui.txtOutBreak_2.setVisible(False)
	self.dlg.ui.txtOutBreak_5.setVisible(False)

	self.dlg.ui.lblGNMale_2.setVisible(False)
	
	

	self.dlg.ui.lblGNArea_2.setVisible(False)
	
	
	global wellReportG
	wellReportG = []

	global BudgetReport
	BudgetReport = []	

	global nWell
	nWell = 0
	global nowWell
	nowWell = 2

	global WellReport
	WellReport = []

	
	global WellGReport
	WellGReport = []

	global rbLepAll
	rbLepAll = []

	global nPop
	nPop = 0
	global nowPop
	nowPop = 2
	global nBug
	nBug = 0
	global nowBug
	nowBug = 2
	
	global nWSource 
	nWSource = 0
	global nowWSource 
	nowWSource = 2

	self.dlg.ui.lblGNArea_4.setVisible(False)
	self.dlg.ui.lblGNArea_3.setVisible(False)

	global xLep
	global yLep
	global rbpL
	global rbLep
	global lyrTempLineLep
	global fidLep

	global childtotList
	childtotList = []

	global givCmb1
	givCmb1 = []

	global givCmb2
	givCmb2 = []

	self.dlg.ui.cmbIDPCampLayerG.setVisible(False)
	self.dlg.ui.cmbIDPCampG.setVisible(False)

	global adultotList
	adultotList = []

	global drugChildQty
	drugChildQty = []

	global drugAdultQty
	drugAdultQty = []

	global adultotList
	adultotList = []

	global childtotList
	childtotList = []
################# End Givanthika #####################

#########################################

	

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/floogin/icontemp.png"),
            u"FLOOgin", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&FLOOgin", self.action)
	#dock
	#self.dock = flooginDialog()
	#self.iface.addDockWidget( Qt.RightDockWidgetArea, self.dock )

	QObject.connect(self.dlg.ui.btnStartR,SIGNAL("clicked()"),self.selectStart)
	QObject.connect(self.dlg.ui.btnStopR,SIGNAL("clicked()"),self.selectStop)
	#Clear Fields
	QObject.connect(self.dlg.ui.btnClearaR,SIGNAL("clicked()"),self.clearFields)
	#Save as image
	##QObject.connect(self.dlg.ui.btnSaveAsaR,SIGNAL("clicked()"),self.saveAs)
	#generate pdf
	QObject.connect(self.dlg.ui.btnGenerateReportR,SIGNAL("clicked()"),self.generateReport)

	#Find routes
	QObject.connect(self.dlg.ui.btnFindRoutesR,SIGNAL("clicked()"),self.findRoutes)
	# connect to the currentLayerChanged signal of QgsInterface
	result = QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer *)"), self.handleLayerChange)

	# dil-IDP
	#select non-affected IDP camps - dil
	QObject.connect(self.dlg.ui.btnNonaffectIDP,SIGNAL("clicked()"),self.selectNonAffecIDP)
	#show attribute table - dil
	##QObject.connect(self.dlg.ui.chkshowAll,SIGNAL("stateChanged(int)"),self.showAttributeTable)	
	#indexchangedin find nearby range - dil
	QObject.connect(self.dlg.ui.cboDisRange,SIGNAL("currentIndexChanged(const QString&)"),self.disRangeIDPIndexChanged);  	
	#select Location to view IDP details -dil
	QObject.connect(self.dlg.ui.btnViewDetIDP,SIGNAL("clicked()"),self.viewIDPDetails)
	#find near by locations - dil
	QObject.connect(self.dlg.ui.btnShwNearIDP,SIGNAL("clicked()"),self.findNearbyIDP)
	#select nearby loc - dil
	QObject.connect(self.dlg.ui.btnSelectIDPLoc,SIGNAL("clicked()"),self.selectIDPLoc)
	#refresh - dil
	#QObject.connect(self.dlg.ui.btnRefreshIDP,SIGNAL("clicked()"),self.refreshIDP)
	#generate map - dil
	QObject.connect(self.dlg.ui.btnGenerateMapIDP,SIGNAL("clicked()"),self.generateMapIDP)
	#generate map manually - dil
	QObject.connect(self.dlg.ui.btnGenerateMapManualyIDP,SIGNAL("clicked()"),self.generateMapManuallyIDP)
	#clearGenMapLayers - dil
	QObject.connect(self.dlg.ui.btnClearLayersIDP,SIGNAL("clicked()"),self.clearGenMapFieldsIDP)
	#Generate map steps up - dil
	QObject.connect(self.dlg.ui.btnPrevStepIDP,SIGNAL("clicked()"),self.stepsUpIDP)
	#Generate map steps down - dil
	QObject.connect(self.dlg.ui.btnNextStepIDP,SIGNAL("clicked()"),self.stepsDownIDP)
	#Clear Fields 2 - dil
	#QObject.connect(self.dlg.ui.btnResetIDP,SIGNAL("clicked()"),self.resetIDP)
	#flood victims - dil
	QObject.connect(self.dlg.ui.btnViewDetailsPopAffected,SIGNAL("clicked()"),self.floodVictimsDetails)
	#clear flood victims - dil
	QObject.connect(self.dlg.ui.btnClearIDPc,SIGNAL("clicked()"),self.clearFloodVictims)
	#clear IDP 1 
	QObject.connect(self.dlg.ui.btnClearIDPa,SIGNAL("clicked()"),self.clearIDPLoc)
	#clear IDP 2 
	QObject.connect(self.dlg.ui.btnClearNearBy,SIGNAL("clicked()"),self.clearIDPNearby)
	#help dialog 1 - dil
	QObject.connect(self.dlg.ui.btnHelpGenMapIDP,SIGNAL("clicked()"),self.helpDialogIDPStart)
	#help dialog 2 - dil
	QObject.connect(self.dlg.ui.btnHelpIDPa,SIGNAL("clicked()"),self.helpDialogIdentifyIDP)
	#help dialog 3 - dil
	QObject.connect(self.dlg.ui.btnHelpIDPb,SIGNAL("clicked()"),self.helpDialogNearByIDP)
	#help dialog 4 - dil
	QObject.connect(self.dlg.ui.btnHelpIDPc,SIGNAL("clicked()"),self.helpDialogVictimIDP)
	#help dialog 5
	QObject.connect(self.dlg.ui.btnHelpIDPAvail,SIGNAL("clicked()"),self.helpDialogavailIDP)
	#close help dialog - dil
	QObject.connect(self.dlgHelpIDP.uiHelpIDP.btnCloseHelpIDP,SIGNAL("clicked()"),self.helpDialogCloseIDP)
	#reset pop comb
	QObject.connect(self.dlg.ui.btnResetpopIDP_2,SIGNAL("clicked()"),self.popResetIDP)
	#report generate IDP
	QObject.connect(self.dlg.ui.btnGenerateReportIDP,SIGNAL("clicked()"),self.generateReportIDP)
	#check capacity IDP
	QObject.connect(self.dlg.ui.btnCheckAvailIDP,SIGNAL("clicked()"),self.checkIDPCapacityAvail)
	#refresh ds layer IDP
	QObject.connect(self.dlg.ui.btnRefreshDSLayerIDP,SIGNAL("clicked()"),self.refreshDSLayerIDP)
	#refresh pop layer IDP
	#QObject.connect(self.dlg.ui.btnRefreshPopLayerIDP,SIGNAL("clicked()"),self.refreshPopLayerIDP)
	#indexchangedin DS layer IDP
	QObject.connect(self.dlg.ui.cmbDSLayerIDP,SIGNAL("currentIndexChanged(const QString&)"),self.dsLayerIndexChanged); 
	#show idp avail capacity
	QObject.connect(self.dlg.ui.btnShowIDPAvail,SIGNAL("clicked()"),self.showIDPAvail) 
	#clear idp avail capacity
	QObject.connect(self.dlg.ui.btnClearIDPAvail,SIGNAL("clicked()"),self.clearIDPAvailCap)
	#Select IDP type
	QObject.connect(self.dlg.ui.btnIDPType,SIGNAL("clicked()"),self.IDPTypeSelect)
	#Lable IDPcamp Type
	QObject.connect(self.dlg.ui.btnLblFeature,SIGNAL("clicked()"),self.LableIDPfeatures)
 	#Clear nonaffected camps
	QObject.connect(self.dlg.ui.btnclearselectnonaffIDP,SIGNAL("clicked()"),self.ClearnonaffecIDP)
	# dil-IDP above

	#Clear Fields 2
	##QObject.connect(self.dlg.ui.btnReset,SIGNAL("clicked()"),self.reset)
	#refresh
	##QObject.connect(self.dlg.ui.btnRefresh,SIGNAL("clicked()"),self.refresh)
	#generate map
	QObject.connect(self.dlg.ui.btnGenerateMap,SIGNAL("clicked()"),self.generateMap)
	#generate map manually
	QObject.connect(self.dlg.ui.btnGenerateMapManualy,SIGNAL("clicked()"),self.generateMapManually)
	#clearGenMapLayers
	QObject.connect(self.dlg.ui.btnClearLayers,SIGNAL("clicked()"),self.clearGenMapFields)
	#Generate map steps up
	QObject.connect(self.dlg.ui.btnPrevStep,SIGNAL("clicked()"),self.stepsUp)
	#Generate map steps down
	QObject.connect(self.dlg.ui.btnNextStep,SIGNAL("clicked()"),self.stepsDown)
	#getDirections
	QObject.connect(self.dlg.ui.btnGetDirectionsR,SIGNAL("clicked()"),self.getdirections)

	#indexchangedin Length metric directions
	QObject.connect(self.dlg.ui.cmbLength2R,SIGNAL("currentIndexChanged(const QString&)"),self.lenMetricIndexChanged);
	#CleargetDirections
	QObject.connect(self.dlg.ui.btnClearbR,SIGNAL("clicked()"),self.ClearGetDir)
	#cursor move
	#QObject.connect(self.curMove, SIGNAL("xyCoordinates( const QgsPoint &p	))"), self.cursorMove)
	#QgsMapCanvas::xyCoordinates 	( 	const QgsPoint &  	p	) 	
	#result = QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDown)
	#QMessageBox.information( self.iface.mainWindow(),"Info", "connect = %s"%str(result) )
	#add tooltips for buttons	
	self.dlg.ui.btnStartR.setToolTip("click here and select a start location on map canvas")
	self.dlg.ui.btnStopR.setToolTip("click here and select a stop location on map canvas")
	self.dlg.ui.btnByCar.setToolTip("By Car")
	self.dlg.ui.btnWalking.setToolTip("Walking")
	self.clickTool.canvasClicked.connect(self.clickedCanvas)
	#indexchangedin stop Hospital layer
	QObject.connect(self.dlg.ui.cmbHospitalLayerR,SIGNAL("currentIndexChanged(const QString&)"),self.stopHospIndexChanged);
	#indexchangedin stop IDP layer
	QObject.connect(self.dlg.ui.cmbIDPCampLayerR,SIGNAL("currentIndexChanged(const QString&)"),self.stopIDPIndexChanged);
	#indexchangedin stop Hospital location 
	##QObject.connect(self.dlg.ui.cmbHospitalR,SIGNAL("currentIndexChanged(const QString&)"),self.stopHospLocIndexChanged);
	QObject.connect(self.dlg.ui.btnHospOk,SIGNAL("clicked()"),self.stopHospLocIndexChanged)
	#indexchangedin stop IDP location 
	##QObject.connect(self.dlg.ui.cmbIDPCampR,SIGNAL("currentIndexChanged(const QString&)"),self.stopIDPLocIndexChanged);
	QObject.connect(self.dlg.ui.btnIDPOk,SIGNAL("clicked()"),self.stopIDPLocIndexChanged)
	#refresh hosp layers
	QObject.connect(self.dlg.ui.btnRefreshHospStop,SIGNAL("clicked()"),self.refreshLayersHosp)	
	#refresh IDP layers
	QObject.connect(self.dlg.ui.btnRefreshIDPStop,SIGNAL("clicked()"),self.refreshLayersIDP)	

	
	#timetotravle- car
	QObject.connect(self.dlg.ui.btnByCar,SIGNAL("clicked()"),self.travelByCar)
	#timetotravle- walk
	QObject.connect(self.dlg.ui.btnWalking,SIGNAL("clicked()"),self.travelWalk)
	#timetotravle - indexchangedin kmh 
	QObject.connect(self.dlg.ui.cmbSpeedOfTravel,SIGNAL("currentIndexChanged(const QString&)"),self.speedIndexChanged);
	#help dialog 
	QObject.connect(self.dlg.ui.btnHelpaR,SIGNAL("clicked()"),self.helpDialogRoute)
	#help dialog first steps 
	QObject.connect(self.dlg.ui.btnHelpGenMap,SIGNAL("clicked()"),self.helpDialogStart)
	#help dialog directions
	QObject.connect(self.dlg.ui.btnHelpbR,SIGNAL("clicked()"),self.helpDialogDirec)
	#help dialog blocked roads
	QObject.connect(self.dlg.ui.btnHelpcR,SIGNAL("clicked()"),self.helpDialogBlock)
	#help dialog blocked roads cat 
	QObject.connect(self.dlg.ui.btnHelpcRBCat,SIGNAL("clicked()"),self.helpDialogBlockCat)
	#close help dialog
	QObject.connect(self.dlgHelp.uiHelp.btnCloseHelp,SIGNAL("clicked()"),self.helpDialogClose)
	#blocked roads
	QObject.connect(self.dlg.ui.btnBlockedRoads,SIGNAL("clicked()"),self.identifyBlockedRoads)
	#clear Blocked roads 
	QObject.connect(self.dlg.ui.btnClearcR,SIGNAL("clicked()"),self.clearBlockedRoads)
	#At a glance 
	QObject.connect(self.dlg.ui.btnOkGlance,SIGNAL("clicked()"),self.atGlnaceRoads)
	#indexchangedin road layer glance
	QObject.connect(self.dlg.ui.cmbRoadLayerGlance,SIGNAL("currentIndexChanged(const QString&)"),self.roadLayerGlanceIndexChanged);
	#At a glance - reset
	QObject.connect(self.dlg.ui.btnResetGlance,SIGNAL("clicked()"),self.atGlnaceRoadsReset)
	#At a glance - refresh
	QObject.connect(self.dlg.ui.btnRefreshGlanceLayer,SIGNAL("clicked()"),self.atGlnaceRoadsRefresh)
	#next tab1
	QObject.connect(self.dlg.ui.btnNext1,SIGNAL("clicked()"),self.nextOne)
	#next tab2
	QObject.connect(self.dlg.ui.btnNext2,SIGNAL("clicked()"),self.nextTwo)
	#next tab3
	QObject.connect(self.dlg.ui.btnNext3,SIGNAL("clicked()"),self.nextThree)
	#show view report road
	QObject.connect(self.dlgViewR.uiViewR.btnOKReport,SIGNAL("clicked()"),self.showReportRoad)	
	#close view repor Road
	QObject.connect(self.dlgViewR.uiViewR.btnNotNowReport,SIGNAL("clicked()"),self.closeViewReportRoad)	
	#save view repor Road
	QObject.connect(self.dlgViewR.uiViewR.btnSaveReportRoad,SIGNAL("clicked()"),self.renameViewReportRoad)
	#email report 	
	QObject.connect(self.dlgViewR.uiViewR.btnEmailRep,SIGNAL("clicked()"),self.emailReportRoad)
	#email report send 	
	QObject.connect(self.dlgEmailR.uiEmailR.btnSendEmailRoad,SIGNAL("clicked()"),self.sendEmailReportRoad)
	#email report clear 	
	QObject.connect(self.dlgEmailR.uiEmailR.btnEmailClear,SIGNAL("clicked()"),self.clearEmailReportRoad)
	#email report exit 	
	QObject.connect(self.dlgEmailR.uiEmailR.btnEmailExit,SIGNAL("clicked()"),self.exitEmailReportRoad)
	#email report gmail 	
	QObject.connect(self.dlgEmailR.uiEmailR.btnGmail,SIGNAL("clicked()"),self.gmailEmailReportRoad)
	#email report hotmail 	
	QObject.connect(self.dlgEmailR.uiEmailR.btnHotmail,SIGNAL("clicked()"),self.hotmailEmailReportRoad)
	#email report yahoo 	
	QObject.connect(self.dlgEmailR.uiEmailR.btnYahoo,SIGNAL("clicked()"),self.yahooEmailReportRoad)
	#lost focus email username 
	self.dlgEmailR.uiEmailR.txtUsernameRep.editingFinished.connect(self.handleEditingFinishedUN)
	#blocked roads categorized - refresh layers 
	QObject.connect(self.dlg.ui.btnRefreshAdminiLyr,SIGNAL("clicked()"),self.refreshAdminisLyrs)
	#blocked roads categorized -  generate map 
	QObject.connect(self.dlg.ui.btnGenMapAdminis,SIGNAL("clicked()"),self.generateAdminisRoadsMap)
	#radio button all checked 
	self.dlg.ui.rdAllBlocked.toggled.connect(self.radioAllSelect)
	#radio button categorized checked 
	self.dlg.ui.rdCatBlocked.toggled.connect(self.radioCatSelect)
	#indexchangedin province 
	QObject.connect(self.dlg.ui.btnProvinceOk,SIGNAL("clicked()"),self.provinceIndexChanged)
	#indexchangedin district 
	QObject.connect(self.dlg.ui.btnDistOk,SIGNAL("clicked()"),self.districtIndexChanged)
	#indexchangedin DS 
	QObject.connect(self.dlg.ui.btnDSOk,SIGNAL("clicked()"),self.dsIndexChanged)
	#indexchangedin GND
	QObject.connect(self.dlg.ui.btnGNDOk,SIGNAL("clicked()"),self.gndIndexChanged)
	#view blocked roads cat 
	QObject.connect(self.dlg.ui.btnViewBlockedroadsCat,SIGNAL("clicked()"),self.identifyBlockedRoadsCat)
	#radio button asc checked 
	self.dlg.ui.rdAscSort.toggled.connect(self.radioAscSort)
	#radio button desc checked 
	self.dlg.ui.rdDescSort.toggled.connect(self.radioDescSort)
	#clear blocked roads cat 
	QObject.connect(self.dlg.ui.btnClearcRBCat,SIGNAL("clicked()"),self.clearBRoadsCat)
	#show on map - directions 
	QObject.connect(self.dlg.ui.btnShowDirOnMap,SIGNAL("clicked()"),self.showDirecOnMap)
	#show help - admin All 
	QObject.connect(self.dlg.ui.btnHelpAll,SIGNAL("clicked()"),self.helpDialogAdminAll)
	#show help - admin cat 
	QObject.connect(self.dlg.ui.btnHelpCat,SIGNAL("clicked()"),self.helpDialogAdminCat)
	#stop showing directions on map 
	QObject.connect(self.dlg.ui.btnStopShowLoc,SIGNAL("clicked()"),self.stopShowPathOnMap)
	#show labelling locations 
	QObject.connect(self.dlg.ui.btnShowLabelling,SIGNAL("clicked()"),self.showLabellingFeatures)
	#hide labelling locations 
	QObject.connect(self.dlg.ui.btnHideLabelling,SIGNAL("clicked()"),self.hideLabellingFeatures)
	#refresh labelling layers 
	QObject.connect(self.dlg.ui.refreshLayerLabelling,SIGNAL("clicked()"),self.refreshLabellingLayers)
	#refresh gen map road layer 
	QObject.connect(self.dlg.ui.btnRefreshRoadLayer,SIGNAL("clicked()"),self.refreshRoadLayer)
	#refresh gen map flood layer 
	QObject.connect(self.dlg.ui.btnRefreshFloodLayer,SIGNAL("clicked()"),self.refreshFloodLayer)
	#print directions in txt 
	QObject.connect(self.dlg.ui.btnDirectionstxt,SIGNAL("clicked()"),self.generatetxtDirec)
	#generate image
	QObject.connect(self.dlg.ui.btnDirectionsImage,SIGNAL("clicked()"),self.genMapForImage)
	#generate report find route
	QObject.connect(self.dlg.ui.btnDirectionsPDF,SIGNAL("clicked()"),self.generateReportFindRoute)
	#directions audio file 
        QObject.connect(self.dlg.ui.btnDirectionsAudio,SIGNAL("clicked()"),self.generateAudioDirections)	
	#draw chart blocked roads 
	QObject.connect(self.dlg.ui.btnSummaryChart,SIGNAL("clicked()"),self.blockedRoadsChart)
	#check Possible Hosp Ok 
	QObject.connect(self.dlg.ui.btnHospOkLyr,SIGNAL("clicked()"),self.checkPossibleHospOk)
	#check Possible Hosp Ok 
	QObject.connect(self.dlg.ui.btnIDPOkLyr,SIGNAL("clicked()"),self.checkPossibleIDPOk)
	#show how Hosp 
	QObject.connect(self.dlg.ui.btnshowDetailsHos,SIGNAL("clicked()"),self.showHowDetailsHos)
	#show how idp 
	QObject.connect(self.dlg.ui.btnshowDetailsIDP,SIGNAL("clicked()"),self.showHowDetailsIDP)

	#************************ Hospitals and Medicinal Resources_Dish***********************************************************#
	#Clear Fields
	QObject.connect(self.dlg.ui.btnClearN,SIGNAL("clicked()"),self.clearFieldsN)
	#Save as image
	QObject.connect(self.dlg.ui.btnSaveAsN,SIGNAL("clicked()"),self.saveAsN)
	#refresh
	#QObject.connect(self.dlg.ui.btnResetN,SIGNAL("clicked()"),self.refresh)
	#generate map
	QObject.connect(self.dlg.ui.btnGenerateMapN,SIGNAL("clicked()"),self.generateMapHos)
	#generate map manually
	QObject.connect(self.dlg.ui.btnGenerateMapManuallyN,SIGNAL("clicked()"),self.generateMapManuallyHos)
	#clearGenMapLayers
	QObject.connect(self.dlg.ui.btnClearN_1,SIGNAL("clicked()"),self.clearGenMapFieldsHos_one)
	QObject.connect(self.dlg.ui.btnClearN_2,SIGNAL("clicked()"),self.clearGenMapFieldsHos_two)
	QObject.connect(self.dlg.ui.btnClearN_3,SIGNAL("clicked()"),self.clearGenMapFieldsHos_three)
	QObject.connect(self.dlg.ui.btnClearN_4,SIGNAL("clicked()"),self.clearGenMapFieldsHos_four)
	#Generate map steps up
	QObject.connect(self.dlg.ui.btnPrevStepN,SIGNAL("clicked()"),self.stepsUpHos)
	#Generate map steps down
	QObject.connect(self.dlg.ui.btnNextStepN,SIGNAL("clicked()"),self.stepsDownHos)
 	#Get the count of non affected Hospitals 
        QObject.connect(self.dlg.ui.chkNonAffected,SIGNAL("stateChanged(int)"),self.methodCall)
       	#Get data to a text file
        QObject.connect(self.dlg.ui.btn_GenerateReports,SIGNAL("clicked()"),self.printData)
	#Display Non Affected Hospitals and Beds
        #QObject.connect(self.dlg.ui.chkNonAffected,SIGNAL("stateChanged(int)"),self.selectNonAffectedHosTabView)
        #Display Available number of doctors in non affected hospitals
        QObject.connect(self.dlg.ui.chknumberofDoctors,SIGNAL("stateChanged(int)"),self.getDocsTabview)
	#Get available Non affected Pharmacies 
        QObject.connect(self.dlg.ui.chkPharmacy,SIGNAL("stateChanged(int)"),self.getPharmacyTabview)
	#Display Names
	QObject.connect(self.dlg.ui.btnShowlbl,SIGNAL("clicked()"),self.LableHospfeatures)
	
	#Get available Non affected clinics       
	QObject.connect(self.dlg.ui.chkboxclinics,SIGNAL("stateChanged(int)"),self.getClinicDetailsTabview)
        #Generate report Hospital details
        QObject.connect(self.dlg.ui.btnGenReportN,SIGNAL("clicked()"),self.generateReportHos)
	QObject.connect(self.dlg.ui.btnGenReportTwo,SIGNAL("clicked()"),self.generateReportHosSearch)
	QObject.connect(self.dlg.ui.btnGenReportN_4,SIGNAL("clicked()"),self.generateReportOtherMed)
	QObject.connect(self.dlg.ui.btnGenReportN_5,SIGNAL("clicked()"),self.generateReportHosGN)
	
        #Help_dish
	QObject.connect(self.dlg.ui.btnHelpN,SIGNAL("clicked()"),self.HelpGenerateMapN)
	QObject.connect(self.dlg.ui.btnHelpN_2,SIGNAL("clicked()"),self.HelpHospDetailsN)
        #generate map for Amin Areas 
	QObject.connect(self.dlg.ui.btnGenMapAdminisN,SIGNAL("clicked()"),self.generateAdminisHosMap)
	#generate map for Amin Areas- refresh layers 
	QObject.connect(self.dlg.ui.btnRefreshAdminiLyr_N,SIGNAL("clicked()"),self.refreshAdminisLyrsN)
	#QObject.connect(self.dlg.ui.btnRefreshAdminiLyrGN,SIGNAL("clicked()"),self.refreshAdminisLyrsHos)

	#Indexchange
	#QObject.connect(self.dlg.ui.cmbAdminLayerGN,SIGNAL("currentIndexChanged(const QString&)"),self.searchHosByGN);
	

	#Search Hospital details
        QObject.connect(self.dlg.ui.btnSearch,SIGNAL("clicked()"),self.searchHos)
	#Get DSGN Areas 
        QObject.connect(self.dlg.ui.chkGN,SIGNAL("stateChanged(int)"),self.GetGNDSHosTabView)

 
 
	#************************ Hospitals and Medicinal Resources_Dish Above***********************************************************#


	########################################### Givanthika ###############################################

	#btnHelpWellPage
	QObject.connect(self.dlg.ui.btnHelpWellPage,SIGNAL("clicked()"),self.wellhepl)

	QObject.connect(self.dlg.ui.btnHelpGenMapSources,SIGNAL("clicked()"),self.wshepl)

	QObject.connect(self.dlg.ui.btnHelpBudgetPage1,SIGNAL("clicked()"),self.budhepl)

	QObject.connect(self.dlg.ui.btnHelpBudgetPage4,SIGNAL("clicked()"),self.budheplUsr) #

	QObject.connect(self.dlg.ui.btnHelpBudgetPage2,SIGNAL("clicked()"),self.budhepl) #

	QObject.connect(self.dlg.ui.btnHelpRisk3,SIGNAL("clicked()"),self.budheplRisk) #btnHelpRisk1

	QObject.connect(self.dlg.ui.btnHelpRisk1,SIGNAL("clicked()"),self.budheplRisk)

	

	#select affected Well
	QObject.connect(self.dlg.ui.chkAffectWell,SIGNAL("stateChanged(int)"),self.selectAffecWell)  

	#selectAffecWSources
	QObject.connect(self.dlg.ui.chkAffectWell_3,SIGNAL("stateChanged(int)"),self.selectAffecWSources) # 

	#show attribute tables
	QObject.connect(self.dlg.ui.chkshowAllAffWell,SIGNAL("stateChanged(int)"),self.showAttributeTable)
	QObject.connect(self.dlg.ui.chkshowAllAffPopDrug,SIGNAL("stateChanged(int)"),self.showAttributeTable)
	QObject.connect(self.dlg.ui.chkshowAllAffWell_3,SIGNAL("stateChanged(int)"),self.showAttributeTable)

	#clearGenMapLayers - Well
	QObject.connect(self.dlg.ui.btnClearLayersWell,SIGNAL("clicked()"),self.clearGenMapFieldsWell)

	#generate map manually - Well
	QObject.connect(self.dlg.ui.btnGenerateMapManualyWell,SIGNAL("clicked()"),self.generateMapManuallyWell)

	#Generate map steps up - Well
	QObject.connect(self.dlg.ui.btnPrevStepWell,SIGNAL("clicked()"),self.stepsUpWell)

	#Generate map steps down - Well
	QObject.connect(self.dlg.ui.btnNextStepWell,SIGNAL("clicked()"),self.stepsDownWell)

	QObject.connect(self.dlg.ui.btnClearWella,SIGNAL("clicked()"),self.clearWellLoc)

	QObject.connect(self.dlg.ui.btnViewAllDetailsWell,SIGNAL("clicked()"),self.viewWellDetails)

	
	#generateMapManuallySource
	QObject.connect(self.dlg.ui.btnGenerateMapManualySources,SIGNAL("clicked()"),self.generateMapManuallySource)

	#Sources
	QObject.connect(self.dlg.ui.btnPrevStepSources,SIGNAL("clicked()"),self.stepsUpWSource)

	#clearSources
	QObject.connect(self.dlg.ui.btnClearLayersSources,SIGNAL("clicked()"),self.clearSources)

	QObject.connect(self.dlg.ui.btnNextStepSources,SIGNAL("clicked()"),self.stepsDownWSource)

	
	QObject.connect(self.dlg.ui.btnViewAllDetailsWS,SIGNAL("clicked()"),self.viewWSDetails)


##### Meducinal Drugs Estimation Functions Calling

	#generate map manually - drug
	QObject.connect(self.dlg.ui.btnGenerateMapManualyDrug,SIGNAL("clicked()"),self.generateMapManuallyDrug)
	
	#clearGenMapLayers - drug
	QObject.connect(self.dlg.ui.btnClearLayersDrug,SIGNAL("clicked()"),self.clearDrugEstimation)
	
	#population details - drug
	QObject.connect(self.dlg.ui.showDetailBtn,SIGNAL("clicked()"),self.showMessage) 

	#btnPrevStepDrug
	QObject.connect(self.dlg.ui.btnPrevStepDrug,SIGNAL("clicked()"),self.stepsUpDrug)

	#Generate map steps up - Budget
	QObject.connect(self.dlg.ui.btnPrevStepBug,SIGNAL("clicked()"),self.stepsUpDrugBug)
	#btnPrevStepDrug
	QObject.connect(self.dlg.ui.btnNextStepBug,SIGNAL("clicked()"),self.stepsDownDrugBug)
		
	QObject.connect(self.dlg.ui.btnNextStepDrug,SIGNAL("clicked()"),self.stepsDownDrug)
	
	#btnResetDrug
	QObject.connect(self.dlg.ui.btnResetDrug,SIGNAL("clicked()"),self.resetDrug)
	
	#countDrug
	QObject.connect(self.dlg.ui.btnAddBudget,SIGNAL("clicked()"),self.countDrug)

	#btnCalc_4
	QObject.connect(self.dlg.ui.btnCalc_4,SIGNAL("clicked()"),self.countDrugTotal)

	
	#btnBugWithDetails budgetWithDetails
	QObject.connect(self.dlg.ui.btnBugWithDetails,SIGNAL("clicked()"),self.calcTotBug)  

	#viewDrugDetails chkViewDrug
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsFever) 

	#viewDrugDetailsCoughARI
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsCoughARI)

	#viewDrugDetailsDiarrhea
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsDiarrhea)

	#viewDrugDetailsVomotting
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsVomotting)
	
	#viewDrugDetailsBacterialDiarrhea
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsBacterialDiarrhea)	

	#viewDrugDetailsMusclePain
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsMusclePain)

	#viewDrugDetailsMisFever
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsMisFever)

	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsFeverHepatis)	

	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsVomottingHepatis)

	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsMusclePainLepatos)

	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsFeverLepatos)

	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsFeverARI)

	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsVomottingARI)

	
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsDiarrheaHepatis)

	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsPenicilineLepatos)

	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsCephalexin)

	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("clicked()"),self.viewDrugDetailsCiprofloxacin)
	

	#viewSubdiseases
	QObject.connect(self.dlg.ui.chkViewSubDiseases,SIGNAL("stateChanged(int)"),self.viewSubdiseases)
	
	#countApprovedDrugTotal
	QObject.connect(self.dlg.ui.btnAddD1,SIGNAL("clicked()"),self.viewDetailsDrug1)
	
	
	QObject.connect(self.dlg.ui.btnAddD3,SIGNAL("clicked()"),self.viewDetailsDrug3)

	QObject.connect(self.dlg.ui.btnAddD4,SIGNAL("clicked()"),self.viewDetailsDrug4)

	QObject.connect(self.dlg.ui.btnAddD2,SIGNAL("clicked()"),self.calcQty1)
	QObject.connect(self.dlg.ui.btnAddD3,SIGNAL("clicked()"),self.calcQty2)
	QObject.connect(self.dlg.ui.btnAddD4,SIGNAL("clicked()"),self.calcQty3)

	#affectedCategories
	QObject.connect(self.dlg.ui.chkAffRiskyY,SIGNAL("clicked()"),self.affectedCategoriestest) 
	
	
	#immunizedProcess
	QObject.connect(self.dlg.ui.btnImmunizedMes,SIGNAL("clicked()"),self.showMessageMeasles)
	QObject.connect(self.dlg.ui.btnToBeVaccined,SIGNAL("clicked()"),self.showMessageMeaslesToVaccine)


	#chkViewDrug
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("stateChanged(int)"),self.selectCondition)

	#selectConditionMisc
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("stateChanged(int)"),self.selectConditionMisc)

	#selectConditionARI
	QObject.connect(self.dlg.ui.chkViewDrug,SIGNAL("stateChanged(int)"),self.selectConditionHepatis)

	#clearAllDrugFields
	QObject.connect(self.dlg.ui.btnClearAll,SIGNAL("clicked()"),self.clearAllDrugFields) 

	#clearAllMisRisk
	QObject.connect(self.dlg.ui.btnClearMis,SIGNAL("clicked()"),self.clearAllMisRisk)

	

	#clearAllManual
	QObject.connect(self.dlg.ui.btnClearAll_2,SIGNAL("clicked()"),self.clearAllManual) 

	QObject.connect(self.dlg.ui.btnWellClear,SIGNAL("clicked()"),self.wellPage)

	QObject.connect(self.dlg.ui.btnWSClear,SIGNAL("clicked()"),self.wsPage)

	#btnClearWella_2
	QObject.connect(self.dlg.ui.btnClearWella_2,SIGNAL("clicked()"),self.popPage)

	#btnGraph
	#QObject.connect(self.dlg.ui.btnGraph,SIGNAL("clicked()"),self.graphDiseases)

	#wsReport
	QObject.connect(self.dlg.ui.btnPdfWS,SIGNAL("clicked()"),self.wsReport)

	QObject.connect(self.dlg.ui.btnPdfWell,SIGNAL("clicked()"),self.wellReport)

	#clearLep
	#QObject.connect(self.dlg.ui.btnClearLep,SIGNAL("clicked()"),self.clearLep) 

	QObject.connect(self.dlg.ui.btnClearLep,SIGNAL("clicked()"),self.riskLepClear)
	QObject.connect(self.dlg.ui.btnClearLep_2,SIGNAL("clicked()"),self.refresrLepresults)

	#refreshResultBud
	QObject.connect(self.dlg.ui.btnClearAll_3,SIGNAL("clicked()"),self.refreshResultBud)
	#selectAffecGNAreas
	QObject.connect(self.dlg.ui.chkAffGND,SIGNAL("stateChanged(int)"),self.selectAffecGNAreas)

	#screenshot screenshotWell
	
	QObject.connect(self.dlg.ui.btnWellPNG,SIGNAL("clicked()"),self.screenshotWell)
	QObject.connect(self.dlg.ui.btnWSPNG,SIGNAL("clicked()"),self.screenshotWS) 
	QObject.connect(self.dlg.ui.btnBudPNG1,SIGNAL("clicked()"),self.screenshotBudget1)
	QObject.connect(self.dlg.ui.btnBudPNG2,SIGNAL("clicked()"),self.screenshotBudget2) 
	QObject.connect(self.dlg.ui.btnBudPNG2_2,SIGNAL("clicked()"),self.screenshotAnalyze1)
	QObject.connect(self.dlg.ui.btnBudPNG2_3,SIGNAL("clicked()"),self.screenshotAnalyze2)
	
	
	#clearFieldsG
	QObject.connect(self.dlg.ui.btnShowLDS,SIGNAL("clicked()"),self.loadHosToBudget) #clearFieldsG loadHosToBudget

	

	#drugsDistribution
	QObject.connect(self.dlg.ui.btnShowGN,SIGNAL("clicked()"),self.drugsDistributionGN)

	QObject.connect(self.dlg.ui.btnShowGNC,SIGNAL("clicked()"),self.drugsDistributionGNC)

	
	QObject.connect(self.dlg.ui.chkAffRiskyY_2,SIGNAL("stateChanged(int)"),self.testgg) #testgg


	
	
	QObject.connect(self.dlg.ui.btnLblFeatureWell,SIGNAL("clicked()"),self.LableWellfeatures1)
	QObject.connect(self.dlg.ui.btnLblFeatureWell_2,SIGNAL("clicked()"),self.LableWellfeatures)

	QObject.connect(self.dlg.ui.btnWellClear,SIGNAL("clicked()"),self.clearWellLocG)
	
	
	QObject.connect(self.dlg.ui.chkAffRiskyY_3,SIGNAL("stateChanged(int)"),self.leppp) 
	QObject.connect(self.dlg.ui.btnShwNearLepHos_2,SIGNAL("clicked()"),self.viewHosAvailabilyty)
	QObject.connect(self.dlg.ui.btnShwNearLepHos_3,SIGNAL("clicked()"),self.viewHosAvailabilyty1)

	
	QObject.connect(self.dlg.ui.chkloadDChild_2,SIGNAL("stateChanged(int)"),self.LoadAllIDP) 

	
	QObject.connect(self.dlg.ui.btnShowGNC_2,SIGNAL("clicked()"),self.idpalloBud)


	QObject.connect(self.dlg.ui.btnClearAll_4,SIGNAL("clicked()"),self.clearmanBugd)
	
	
	################### End Giv###########################################


     ########################################## Givanthika Functions  

    def budheplRisk(self):
	try:

		self.dlgHelpHos.show()
	        self.dlgHelpHos.uiHelpHos.tbwHos.setCurrentIndex(7)
	        self.dlgHelpHos.exec_()
	except:
		print 'help'
 

    def budheplUsr(self):
	try:

		self.dlgHelpHos.show()
	        self.dlgHelpHos.uiHelpHos.tbwHos.setCurrentIndex(4)
	        self.dlgHelpHos.exec_()
	except:
		print 'help'

    def budhepl(self):
	try:

		self.dlgHelpHos.show()
	        self.dlgHelpHos.uiHelpHos.tbwHos.setCurrentIndex(3)
	        self.dlgHelpHos.exec_()
	except:
		print 'help'

    def wshepl(self):
	try:

		self.dlgHelpHos.show()
	        self.dlgHelpHos.uiHelpHos.tbwHos.setCurrentIndex(6)
	        self.dlgHelpHos.exec_()
	except:
		print 'help'

    def wellhepl(self):
	try:

		self.dlgHelpHos.show()
	        self.dlgHelpHos.uiHelpHos.tbwHos.setCurrentIndex(6)
	        self.dlgHelpHos.exec_()
	except:
		print 'help'

    def clearmanBugd(self):
	self.dlg.ui.textBrowser.clear()

    def clearWellLocG(self):	
	try:		
		global gWellLoc
		self.canvas.scene().removeItem(gWellLoc)
	except:
		e = sys.exc_info()
		print e

    def LableWellfeatures(self):
	
	layerr = self.iface.mapCanvas().currentLayer()						
	showFieldd ='Depth' 
	palyr = QgsPalLayerSettings()
	palyr.readFromLayer(layerr)
	palyr.enabled = True 
	palyr.fieldName = showFieldd
	palyr.placement = QgsPalLayerSettings.AroundPoint
	palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
	palyr.writeToLayer(layerr)
	self.iface.mapCanvas().refresh()

    def LableWellfeatures1(self):
	
	layerr = self.iface.mapCanvas().currentLayer()						
	showFieldd ='name' 
	palyr = QgsPalLayerSettings()
	palyr.readFromLayer(layerr)
	palyr.enabled = True 
	palyr.fieldName = showFieldd
	palyr.placement = QgsPalLayerSettings.AroundPoint
	palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
	palyr.writeToLayer(layerr)
	self.iface.mapCanvas().refresh()

    def LableWSfeatures(self):
	
	layerr = self.iface.mapCanvas().currentLayer()						
	showFieldd ='name' 
	palyr = QgsPalLayerSettings()
	palyr.readFromLayer(layerr)
	palyr.enabled = True 
	palyr.fieldName = showFieldd
	palyr.placement = QgsPalLayerSettings.AroundPoint
	palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
	palyr.writeToLayer(layerr)
	self.iface.mapCanvas().refresh()


    def stepsUpWell(self): 
	stepz = self.genMapStepsWell() 
	global nowWell
	nowWell = nowWell - 1
	global nWell
	nWell = nWell - 1
	if nowWell < 1:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[0])
		nIDP = 1
	if nowWell == 1:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[0])
	if nowWell == 2:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[1])
	if nowWell == 3:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[2])
	if nowWell == 4:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[3])
	if nowWell == 5:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[4])
	if nowWell == 6:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[5])
	if nowWell == 7:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[6])
	if nowWell == 8:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[7])
	
    def stepsDownWell(self):
	stepz = self.genMapStepsWell()
	global nowWell
	global nWell
	nWell = nWell + 1
	
	if nWell == 1:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[0])
		nowWell = 1
	if nWell == 2:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[1])
		nowWell = 2
	if nWell == 3:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[2])
		nowWell = 3
	if nWell == 4:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[3])
		nowWell = 4
	if nWell == 5:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[4])
		nowWell = 5
	if nWell == 6:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[5])
		nowWell = 6
	if nWell == 7:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[6])
		nowWell = 7
	if nWell > 8:
		self.dlg.ui.txtFirstStepsWell.setText(stepz[7])
		nowWell = 7

	

    def genMapStepsWell(self): 
	steps = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>' 
	one = "<b>Step 1</b> : Load the " + clBl + "flood-hazard layer " + clBls
	two = "<b>Step 2</b> : Load the " + clBl + "well layer " + clBls
	three = "<b>Step 3</b> : Select the flood hazard layer " + clBl + "from the drop down " + clBls
	four = "<b>Step 4</b> : Select the well layer " + clBl + "from the drop down " + clBls
	five = "<b>Step 5</b> : Give suitable name to the " + clBl + "output map layer " + clBls
	six = "<b>Step 6</b> : Then generate the  " + clBl + "map for process " + clBls
	seven = "<b>Step 7</b> : The generated " + clBl + "flood-affected " + clBls + "layer will be automatically loaded to the TOC and will be saved in your " + clBl + "/home " + clBls + "directory "
	eight = clR + "<b><h3>Now you can start</h3></b> " + clRs  	

	self.dlg.ui.txtFirstStepsWell.clear()	
	steps.append(one)
	steps.append(two)
	steps.append(three)
	steps.append(four)
	steps.append(five)
	steps.append(six)
	steps.append(seven)
	steps.append(eight)
	
	return steps


    def generateMapManuallyWell(self):
	WellLayer = self.dlg.ui.cboWellLayer.currentText()	
	global floodLayer
	global WellPath
	global fdPathWell
	floodLayer = self.dlg.ui.cboFloodLayerWell.currentText()
	outputFile = self.dlg.ui.leOutputFileWell.text()
	allLayersList = self.canvas.layers()
 	for getLayer in allLayersList:
		if str(getLayer.name()) == str(WellLayer):
			WellPath = str(getLayer.source())
			
		elif str(getLayer.name()) == str(floodLayer):
			fdPathWell = str(getLayer.source())
	
	floodVectorLayer = QgsVectorLayer(WellPath, "flood_layer", "ogr")
	wellVectorLayer = QgsVectorLayer(fdPathWell, "well_layer", "ogr")

	output = os.path.splitext(WellPath)[0]
	output += '_'+outputFile+'.shp'



	overlayAnalyzer = QgsOverlayAnalyzer()
	overlayAnalyzer.intersection(floodVectorLayer, wellVectorLayer, output) 

	wb = QgsVectorLayer(output, outputFile, 'ogr')
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
	else:
		print "No layer found"

	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		if str(getLayerNew.name()) == str(outputFile):
			legend.setLayerVisible(getLayerNew, True)
		elif str(getLayerNew.name()) == str(floodLayer):
			legend.setLayerVisible(getLayerNew, True)
		else: 
			legend.setLayerVisible(getLayerNew, False)

 
    def wellArrayG(self):
	global wellArray
	wellArray = [str(WID), str(WName) , str(WOwner) , str(WDepth)]
	for x in range(0, len(wellArray)):
		detailsWell.append

    def selectAffecWell(self,state): 

	self.dlg.ui.lblWellId.setVisible(True)
	self.dlg.ui.lblPlaceWell.setVisible(True)
	self.dlg.ui.lblOwnnerWell.setVisible(True)
	self.dlg.ui.lbldepthWell.setVisible(True)
	

	countWellG = 0 
	self.cLayer = self.canvas.currentLayer()
	i = 0
	global gWellLocAll 
	gWellLocAll = []

	style = getSampleStyleSheet() 
	pdf = SimpleDocTemplate("Affected Well Details - FLOOgin Report.pdf")
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h1>'
	wellReportG.append( h2 + clR + "<b>Affected Well  - FLOOgin Report </b>" + clRs + h2s )
	
	global detailsBudget
	detailsBudget = []

	crs = str(self.iface.activeLayer().crs().authid())
	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")
	time = now.strftime("%H:%M")

	detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " 
	detDateTime = "Generated on : " + date + " at " + time
	detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
	global wellReportG
	wellReportG =[]

	

	global storyWelRep
	storyWelRep = []
	global wellReport
	wellReportG =[]
	global detailsWell
	detailsWell = []	

	
        self.cLayer = self.canvas.currentLayer()  
	tb='<table style="width:500px"><tr><th width="100" align="left">Well ID</th><th></th><th width="100" align="left">Place</th><th width="100" align="left">Owner Name</th><th width="100" align="left">Depth</th></tr>'
	wellReportG.append( ['Well ID','Place', 'Owner Name','Depth'] )
	styles = getSampleStyleSheet()
	nm = Paragraph('''<b>Well ID</b>''',styles["Normal"])
	tp = Paragraph('''<b>Place</b>''',styles["Normal"])
	cs = Paragraph('''<b>Owner Name</b>''',styles["Normal"])
	md = Paragraph('''<b>Depth</b>''',styles["Normal"])
	#pd = Paragraph('''<b>Price</b>''',styles["Normal"])
	detailsBudget.append( [ nm, tp,cs,md] )
	self.dlg.setdetailfill(tb)

        if (state==Qt.Checked):
            for feature in self.cLayer.getFeatures():
			WellType = self.getFieldWell(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'Well':
				fid=feature.id()
				point = geom.asPoint()
				print point
				

				
				name = self.getFieldWellPlace(self.cLayer)
				OwnerName = self.getFieldOwnerName(self.cLayer)
				depth = self.getFieldDepth(self.cLayer)
				ID = self.getFieldWellID(self.cLayer)
				WName = feature[name]
				WOwner = feature[OwnerName]
				WDepth = feature[depth]
				WID = feature[ID]
				b=str(WName)
				c = str(WOwner)
				d = str(WDepth)
				e = str(WID)
				
				self.dlg.listdetailfillWell('<tr><td width="75">' + e + '</td><td width="75">' + b + '</td><td></td><td width="75">' + c + '</td><td width="75">' + d + '</td><</tr>')	
				wellReportG.append( [str(WID), str(WName) , str(WOwner),str(WDepth)] )	
				
				detailsBudget.append( [str(WID), str(WName) , str(WOwner) , str(WOwner) ] )

				tbWell = Table(detailsBudget)
				storyWelRep.append( tbWell ) 
				pdf.build(storyWelRep)		
	
			else:
				caps = self.cLayer.dataProvider().capabilities()
		
		
			
	print "test"

    def showAttributeTable(self,state):
	if (state==Qt.Checked):
		self.cLayer = self.canvas.currentLayer() 
		self.iface.showAttributeTable(self.cLayer)	


     
    def getFieldWellPlace(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldWellPlace = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "name"
			words = colHeadLower.split()
			if term in words:
				fieldWellPlace = colHead
			d = d + 1
		if fieldWellPlace == '':
			fieldWellPlace = str(fields.field(2).name())
		return fieldWellPlace

    def getFieldWellID(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldWellID = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "wellID"
			words = colHeadLower.split()
			if term in words:
				fieldWellID = colHead
			d = d + 1
		if fieldWellID == '':
			fieldWellID = str(fields.field(4).name())
		return fieldWellID


    def getFieldWell(self, layer): 
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldWell = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldWell = colHead
			d = d + 1
		if fieldWell == '':
			fieldWell = str(fields.field(3).name())
		return fieldWell

    def getFieldOwnerName(self, layer): 
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldWellOwner = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for e in string.punctuation:
				colHeadLower= colHeadLower.replace(e," ")
			term = "OwnerName"
			words = colHeadLower.split()
			if term in words:
				fieldWellOwner = colHead
			d = d + 1
		if fieldWellOwner == '':
			fieldWellOwner = str(fields.field(2).name())
		return fieldWellOwner


    def getFieldDepth(self, layer): 
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldWellDepth = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "Depth"
			words = colHeadLower.split()
			if term in words:
				getFieldDepth = colHead
			d = d + 1
		if fieldWellDepth == '':
			fieldWellDepth = str(fields.field(3).name())
		return fieldWellDepth


    def handleMouseDownWellDetails(self, point, button):
       global xWellDetails
       global yWellDetails		
       xWellDetails=float(str(point.x()))
       yWellDetails=float(str(point.y()))		

       pntGeom = QgsGeometry.fromPoint(point)
       pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       rect = pntBuff.boundingBox()
       cLayer = self.canvas.currentLayer()
       selectList = []
       if cLayer:
	       self.markStartWellDetails()
               provider = cLayer.dataProvider()
               feat = QgsFeature()
               
	       request = QgsFeatureRequest().setFilterRect(rect)
	       
	       for feature in cLayer.getFeatures(request):
		       
	               feature = cLayer.getFeatures(request).next()
               
	               global fidWellDetails
                       fidWellDetails=feature.id()
	       
                       self.updateTextBrowserWellDetails()

       else:
               QMessageBox.information( self.iface.mainWindow(),"Info", "No layer currently selected in TOC" ) 


    def handleMouseDownLepHosLoc(self, point, button):
        
	self.labelPos.clear()
        cLayer = self.canvas.currentLayer()
	cLayer.removeSelection()
	self.dlg.ui.txtLocNameLep.clear()
        self.dlg.ui.txtLocNameLep.setText( "<b>X :</b> "+str(point.x()) + " , <b>Y</b> : " +str(point.y()) )
	global xWellDetails
	global yWellDetails		
	xWellDetails=float(str(point.x()))
	yWellDetails=float(str(point.y()))		

	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownLepHosLoc)

    def handleMouseDownLepHosName(self, point, button):
       
       pntGeom = QgsGeometry.fromPoint(point)
       
       pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       rect = pntBuff.boundingBox()
       
       cLayer = self.canvas.currentLayer()
       selectList = []
       if cLayer:
	       self.markStartWellDetails()
               provider = cLayer.dataProvider()
               feat = QgsFeature()
              
	       request = QgsFeatureRequest().setFilterRect(rect)
	       
	       for feature in cLayer.getFeatures(request):
		       
	               feature = cLayer.getFeatures(request).next()
               
	               global fidLep
                       fidLep=feature.id()
	       
                       self.updateTextBrowserIDP()

       else:
               QMessageBox.information( self.iface.mainWindow(),"Info", "No layer currently selected in TOC" ) 

    def updateTextBrowserLep(self):
    	
	global fidLep
        if(fidLep!=0):
		cLayer = self.canvas.currentLayer()
            	self.provider = cLayer.dataProvider()
		
		request = QgsFeatureRequest().txtLocCodiLep(fidLep)
		feature = cLayer.getFeatures(request).next()
                self.dlg.ui.txtLocCodiLep.clear()
		fields = cLayer.pendingFields()
		boldOpp = '<b>'
		boldCll = '</b>'
		
		fieldNm = self.getFieldOwnerName(cLayer)
	   	featrGot = feature[fieldNm]
		featr = str(fieldNm) + " : " + str(featrGot)   

		global startNameLep
		startNameLep = "<b>Location</b> : " + str(featr)
                			
		self.dlg.ui.txtLocCodiLep.setText(str(startNameLep))
		
        	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownLepHosName)
    

    def selectLepHosLoc(self):
	self.labelPos.clear()
	global stopPlace
	stopPlace = 1	
	self.place()
    
      	QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownLepHosLoc)
             
        QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownLepHosName)
     

    def viewWellDetails(self):
	QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownWellDetails)


    def markStartWellDetails(self):
	global xWellDetails
	global yWellDetails
	global mWellDetails
	mWellDetails = QgsVertexMarker(self.canvas)
	mWellDetails.setCenter(QgsPoint(xWellDetails,yWellDetails))
	mWellDetails.setColor(QColor(0,0,255))
	mWellDetails.setIconSize(6)
        mWellDetails.setIconType(QgsVertexMarker.ICON_X) 
        mWellDetails.setPenWidth(5)


    def updateTextBrowserWellDetails(self):
	global fidWellDetails
        if(fidWellDetails!=0):
		cLayer = self.canvas.currentLayer()
            	self.provider = cLayer.dataProvider()
		request = QgsFeatureRequest().setFilterFid(fidWellDetails)
		feature = cLayer.getFeatures(request).next()
                self.dlg.ui.txtWellPoint.clear()
		fields = cLayer.pendingFields()
		boldOpp = '<b>'
		boldCll = '</b>'

		fCountt = fields.count()
		d = 0
		while d < fCountt:
			colHd = str(fields.field(d).name())
			Col = boldOpp + str(colHd) + boldCll + " : " + str(feature[colHd]) + "\n"
			self.dlg.ui.txtWellPoint.append(str(Col))
			d = d + 1
		

		
        	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownWellDetails)

    def clearGenMapFieldsWell(self):
	self.dlg.ui.leOutputFileWell.clear()
	self.dlg.ui.cboWellLayer.clear()
        self.dlg.ui.cboFloodLayerWell.clear()

	allLayersIn = self.canvas.layers()
 	for LayerNow in allLayersIn:	
		self.dlg.ui.cboWellLayer.addItem(LayerNow.name())
                self.dlg.ui.cboFloodLayerWell.addItem(LayerNow.name())
	colRd = '<font color="red">'
	colRds = '</font>'
	self.dlg.ui.txtFirstStepsWell.clear()
	self.dlg.ui.txtFirstStepsWell.setText(colRd + "<b>Please follow these steps</b>" + colRds + '\n' + "<b>(Press on down arrow to start)</b>")
	global nWell
	nWell = 0
	global nowWell
	nowWell = 2

    def clearWellLoc(self):
	self.dlg.ui.txtDetailsa.clear()	
	self.dlg.ui.txtDetailsa.clear()
	self.dlg.ui.chkAffectWell.setChecked(False)
	self.dlg.ui.chkshowAllAffWell.setChecked(False)
	try:		
		global mWellLoc
		self.canvas.scene().removeItem(mWellLoc)
	except:
		e = sys.exc_info()
		print e

    def wellReport(self) :
	QMessageBox.information( self.iface.mainWindow(),"Info", "Saved at /home/Affected Well Details - FLOOgin Report.pdf")

    


##############End well functions *****************

######## Water Sources #########
   

    def stepsUpWSource(self): 
	stepz = self.genMapStepsWSources() 
	global nowWSource
	nowWSource = nowWSource - 1
	global nWSource
	nWSource = nWSource - 1
	if nowWSource < 1:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[0])
		nWSource = 1
	if nowWSource == 1:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[0])
	if nowWSource == 2:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[1])
	if nowWSource == 3:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[2])
	if nowWSource == 4:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[3])
	if nowWSource == 5:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[4])
	if nowWSource == 6:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[5])
	if nowWSource == 7:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[6])
	if nowWSource == 8:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[7])
	

    def stepsDownWSource(self): 
	stepz = self.genMapStepsWSources()
	global nowWSource
	global nWSource
	nWSource = nWSource + 1
	
	if nWSource == 1:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[0])
		nowWSource = 1
	if nWSource == 2:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[1])
		nowWSource = 2
	if nWSource == 3:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[2])
		nowWSource = 3
	if nWSource == 4:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[3])
		nowWSource = 4
	if nWSource == 5:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[4])
		nowWSource = 5
	if nWSource == 6:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[5])
		nowWSource = 6
	if nWSource == 7:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[6])
		nowWSource = 7
	if nWSource > 8:
		self.dlg.ui.txtFirstStepsSources.setText(stepz[6])
		nowWSource = 8

    def genMapStepsWSources(self): 
	steps = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>' 
	one = "<b>Step 1</b> : Load the " + clBl + "flood-hazard layer " + clBls
	two = "<b>Step 2</b> : Load the " + clBl + "water source layer " + clBls
	three = "<b>Step 3</b> : Select the flood hazard layer " + clBl + "from the drop down " + clBls
	four = "<b>Step 4</b> : Select the water source layer " + clBl + "from the drop down " + clBls
	five = "<b>Step 5</b> : Give suitable name to the " + clBl + "output map layer " + clBls
	six = "<b>Step 6</b> : Then generate the  " + clBl + "map for process " + clBls
	seven = "<b>Step 7</b> : The generated " + clBl + "flood-affected " + clBls + "layer will be automatically loaded to the TOC and will be saved in your " + clBl + "/home " + clBls + "directory "
	eight = clR + "<b><h3>Now you can start</h3></b> " + clRs  	

	self.dlg.ui.txtFirstStepsWell.clear()	
	steps.append(one)
	steps.append(two)
	steps.append(three)
	steps.append(four)
	steps.append(five)
	steps.append(six)
	steps.append(seven)
	steps.append(eight)
	
	return steps

    def generateMapManuallySource(self):
	WSourceLayer = self.dlg.ui.cboSourcesLayer.currentText()	
	global floodLayer
	global WSourcePath
	global fdPathWSource
	floodLayer = self.dlg.ui.cboFloodLayerSources.currentText()
	outputFile = self.dlg.ui.leOutputFileSources.text()
	allLayersList = self.canvas.layers()
 	for getLayer in allLayersList:
		if str(getLayer.name()) == str(WSourceLayer):
			WSourcePath = str(getLayer.source())

		elif str(getLayer.name()) == str(floodLayer):
			fdPathWSource = str(getLayer.source())
	
	floodVectorLayer = QgsVectorLayer(WSourcePath, "flood_layer", "ogr")
	wsourceVectorLayer = QgsVectorLayer(fdPathWSource, "Water_sources_layer", "ogr")

	output = os.path.splitext(WSourcePath)[0]
	output += '_'+outputFile+'.shp'

	

	overlayAnalyzer = QgsOverlayAnalyzer()
	overlayAnalyzer.intersection(floodVectorLayer, wsourceVectorLayer, output) 

	
	wb = QgsVectorLayer(output, outputFile, 'ogr')
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
	else:
		print "No layer found"

	#active new layer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		if str(getLayerNew.name()) == str(outputFile):
			legend.setLayerVisible(getLayerNew, True)
		elif str(getLayerNew.name()) == str(floodLayer):
			legend.setLayerVisible(getLayerNew, True)
		else: 
			legend.setLayerVisible(getLayerNew, False)


    def selectAffecWSources(self,state): 
	style = getSampleStyleSheet() 
	pdf = SimpleDocTemplate("Affected Water Source Details - FLOOgin Report.pdf")
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h1>'
	detailsWS.append( h2 + clR + "<b>Affected Water Source Details - FLOOgin Report </b>" + clRs + h2s )
	
	global WatesSourcesLyrForRpt

	global storyWSRep
	storyWSRep = []
	global wsReport
	wsReport =[]
	global detailsWS
	detailsWS = []

	crs = str(self.iface.activeLayer().crs().authid())
	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")
	time = now.strftime("%H:%M")

	detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " 
	detDateTime = "Generated on : " + date + " at " + time
	detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
	detailsWS.append(str(detHazard))
	detailsWS.append(str(detDateTime))
	detailsWS.append(str(detCrs))

	global WSourceReport
	WSourceReport = []
        self.cLayer = self.canvas.currentLayer()  
	tb='<table style="width:500px"><tr><th width="200" align="left">Name</th><th></th><th width="200" align="left">Type</th></tr>'
	WSourceReport.append( ['Name', 'Type'] )
	styles = getSampleStyleSheet()
	nm = Paragraph('''<b>NAME</b>''',styles["Normal"])
	tp = Paragraph('''<b>Unit Type</b>''',styles["Normal"])
	wsReport.append( [ nm, tp] )
	self.dlg.listPopDetailWaterSource(tb) 
        if (state==Qt.Checked):
            for feature in self.cLayer.getFeatures():
			WaterSourceType = self.getFieldWSourceType(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'river' or Type == 'stream':
				fid=feature.id()
				point = geom.asPoint()
				print point
				global mWSLoc
		       		
				name = self.getFieldWSName(self.cLayer)
				WSType = feature['type']
				WSName = feature[name]
				a=str(WSType)
				b=str(WSName)
				self.dlg.listPopDetailWaterSource('<tr><td width="200">' + b + '</td><td></td><td width="200">' + a + '</td></tr>')	
				WSourceReport.append( [str(WSName), str(WSType) ] )	

				wsReport.append( [str(WSName), str(WSType) ] )

				tbWS = Table(wsReport)
				storyWSRep.append( tbWS ) 
				pdf.build(storyWSRep)			
				
	
			else:
				
				caps = self.cLayer.dataProvider().capabilities()
				
	    print "test"

    def getFieldWSName(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldWSName = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "name"
			words = colHeadLower.split()
			if term in words:
				fieldWSName = colHead
			d = d + 1
		if fieldWSName == '':
			fieldWSName = str(fields.field(1).name())
		return fieldWSName
    

    def getFieldWSourceType(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldWSourceType = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldWSourceType = colHead
			d = d + 1
		if fieldWSourceType == '':
			fieldWSourceType = str(fields.field(2).name())
		return fieldWSourceType

    def handleMouseDownWSDetails(self, point, button):
       global xWSDetails
       global yWSDetails		
       xWSDetails=float(str(point.x()))
       yWSDetails=float(str(point.y()))		

       pntGeom = QgsGeometry.fromPoint(point)
       pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       rect = pntBuff.boundingBox()
       cLayer = self.canvas.currentLayer()
       selectList = []
       if cLayer:
	       self.markStartWSDetails()
               provider = cLayer.dataProvider()
               feat = QgsFeature()
               
	       request = QgsFeatureRequest().setFilterRect(rect)
	       
	       for feature in cLayer.getFeatures(request):
		       
	               feature = cLayer.getFeatures(request).next()
               
	               global fidWSDetails
                       fidWSDetails=feature.id()
	       
                       self.updateTextBrowserWSDetails()

       else:
               QMessageBox.information( self.iface.mainWindow(),"Info", "No layer currently selected in TOC" )     

  
    def markStartWSDetails(self):
	global xWSDetails
	global yWSDetails
	global mWSDetails
	mWSDetails = QgsVertexMarker(self.canvas)
	mWSDetails.setCenter(QgsPoint(xWSDetails,yWSDetails))
	mWSDetails.setColor(QColor(0,0,255))
	mWSDetails.setIconSize(6)
        mWSDetails.setIconType(QgsVertexMarker.ICON_X) 
        mWSDetails.setPenWidth(5)

    
    def updateTextBrowserWSDetails(self):
	global fidWSDetails
        if(fidWSDetails!=0):
		cLayer = self.canvas.currentLayer()
            	self.provider = cLayer.dataProvider()
		request = QgsFeatureRequest().setFilterFid(fidWSDetails)
		feature = cLayer.getFeatures(request).next()
                self.dlg.ui.txtWSPoint.clear()
		fields = cLayer.pendingFields()
		boldOpp = '<b>'
		boldCll = '</b>'

		fCountt = fields.count()
		d = 0
		while d < fCountt:
			colHd = str(fields.field(d).name())
			Col = boldOpp + str(colHd) + boldCll + " : " + str(feature[colHd]) + "\n"
			self.dlg.ui.txtWSPoint.append(str(Col))
			d = d + 1
		

		
        	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownWSDetails)

    def viewWSDetails(self):
	QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownWSDetails)

    def wsReport(self) :
	QMessageBox.information( self.iface.mainWindow(),"Info", "Saved at /home/Affected Water Sources Details - FLOOgin Report.pdf")



    def clearSources(self):
	self.dlg.ui.cboSourcesLayer.clear()
	self.dlg.ui.cboFloodLayerSources.clear()
	self.dlg.ui.leOutputFileSources.clear()

	allLayersIn = self.canvas.layers()
 	for LayerNow in allLayersIn:	
		self.dlg.ui.cboSourcesLayer.addItem(LayerNow.name())
                self.dlg.ui.cboFloodLayerSources.addItem(LayerNow.name())
	colRd = '<font color="red">'
	colRds = '</font>'
	self.dlg.ui.txtFirstStepsSources.clear()
	self.dlg.ui.txtFirstStepsSources.setText(colRd + "<b>Please follow these steps</b>" + colRds + '\n' + "<b>(Press on down arrow to start)</b>")
	global nSource
	nSource = 0
	global nowSource
	nowSource = 2

    
########### charts

    def getFieldProvince(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldProvince = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "PROVINCE_N"
			words = colHeadLower.split()
			if term in words:
				fieldProvince = colHead
			d = d + 1
		if fieldProvince == '':
			fieldProvince = str(fields.field(0).name())
		return fieldProvince
   
    def getFieldLepF(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldLepF = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "1_Bk_LepF"
			words = colHeadLower.split()
			if term in words:
				fieldLepF = colHead
			d = d + 1
		if fieldLepF == '':
			fieldLepF = str(fields.field(5).name())
		return fieldLepF

    def getFieldLepM(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldLepM = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "1_Bk_LepM"
			words = colHeadLower.split()
			if term in words:
				fieldLepM = colHead
			d = d + 1
		if fieldLepM == '':
			fieldLepM = str(fields.field(6).name())
		return fieldLepM

    def getFieldLepC(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldLepC = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "1_Bk_LepC"
			words = colHeadLower.split()
			if term in words:
				fieldLepC = colHead
			d = d + 1
		if fieldLepC == '':
			fieldLepC = str(fields.field(7).name())
		return fieldLepC

    def analyseLepG(self,layer):
            for feature in self.cLayer.getFeatures():
			#WellType = self.getFieldProvince(self.cLayer) 						
			#Type = feature['PROVINCE_N']
				geom = feature.geometry()
			#if Type == 'Western':
				fid=feature.id()
				point = geom.asPoint()
				print point
				
				lep = self.getFieldLepF(self.cLayer)
				ARI = self.getFieldLepM(self.cLayer)
				mes = self.getFieldLepC(self.cLayer)
				
				Wlep = feature[lep]
				WARI = feature[ARI]
				Wmes = feature[mes]
				b=str(Wlep)
				c = str(WARI)
				d = str(Wmes)
				
				self.dlg.listdetailfillWell('<tr><td width="100">' + b + '</td><td></td><td width="100">' + c + '</td><td width="100">' + d + '</td><</tr>')	
				WellReport.append( [str(Wlep), str(WARI) , str(Wmes)] )	
	
			#else:
				
				#caps = self.cLayer.dataProvider().capabilities()
				
	    
	    print "test"


    def lepChart (self) :
	for feature in self.cLayer.getFeatures():
			#pro = self.getFieldProvince(self.cLayer) 						
			#Type = feature['PROVINCE_N']
				geom = feature.geometry()
			#if Type == 'Western':
				fid=feature.id()
				point = geom.asPoint()
				print point
				
				lep = self.getFieldLepF(self.cLayer)
				ARI = self.getFieldLepM(self.cLayer)
				mes = self.getFieldLepC(self.cLayer)
				
				Wlep = feature[lep]
				WARI = feature[ARI]
				Wmes = feature[mes]	

	frac = [float(Wlep), float(WARI), float(Wmes)]
	labels = ['Leptospirosis', 'Measles', 'ARI']
	explode = [0, 0.25, 0, 0, 0]

	

	# Create pie chart
	pie(frac, explode, labels, shadow=False)
	# Give it a title
	title('A Sample Pie Chart')
	# save the plot to a PDF file rather than
	# display on screen
	savefig('pichart.pdf', dpi=200, format='PDF')




    

    def screenshot(self):
	w = gtk.gdk.get_default_root_window()
	sz = w.get_size()
	print "The size of the window is %d x %d" % sz
	pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
	pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
	if (pb != None):
    		pb.save("screenshot.png","png")
    		print "Screenshot saved to screenshot.png."
	else:
    		print "Unable to get the screenshot."
	

    def screenshotWell(self):
	w = gtk.gdk.get_default_root_window()
	sz = w.get_size()
	print "The size of the window is %d x %d" % sz
	pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
	pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
	if (pb != None):
    		pb.save("Floogin - Affected Well Details.png","png")
    		print "Screenshot saved to Floogin - Affected Well Details.png."
	else:
    		print "Unable to get the screenshot."
	QMessageBox.information( self.iface.mainWindow(),"Info", "Saved at /home/Floogin - Affected Well Details.png")


    def screenshotAnalyze1(self):
	w = gtk.gdk.get_default_root_window()
	sz = w.get_size()
	print "The size of the window is %d x %d" % sz
	pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
	pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
	if (pb != None):
    		pb.save("Floogin - Measles - Risk Analyze.png","png")
    		print "Screenshot saved to Floogin - Measles - Risk Analyze.png."
	else:
    		print "Unable to get the screenshot."
	QMessageBox.information( self.iface.mainWindow(),"Info", "Saved at /home/Floogin - Measles - Risk Analyze.png")

    def screenshotAnalyze2(self):
	w = gtk.gdk.get_default_root_window()
	sz = w.get_size()
	print "The size of the window is %d x %d" % sz
	pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
	pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
	if (pb != None):
    		pb.save("Floogin - Leptospirosis - Risk Analyze.png","png")
    		print "Screenshot saved to Floogin - Leptospirosis - Risk Analyze.png."
	else:
    		print "Unable to get the screenshot."
	QMessageBox.information( self.iface.mainWindow(),"Info", "Saved at /home/Floogin - Leptospirosis - Risk Analyze.png")


    def screenshotWS(self):
	w = gtk.gdk.get_default_root_window()
	sz = w.get_size()
	print "The size of the window is %d x %d" % sz
	pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
	pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
	if (pb != None):
    		pb.save("Floogin - Affected Water Sources Details.png","png")
    		print "Screenshot saved to Floogin - Affected Water Sources Details.png."
	else:
    		print "Unable to get the screenshot."
	QMessageBox.information( self.iface.mainWindow(),"Info", "Saved at /home/Floogin - Affected Water Sources Details.png")


    def screenshotBudget1(self):
	w = gtk.gdk.get_default_root_window()
	sz = w.get_size()
	print "The size of the window is %d x %d" % sz
	pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
	pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
	if (pb != None):
    		pb.save("Floogin - Budget For Medicinal Drugs With Pre-defined Details.png","png")
    		print "Screenshot saved to Floogin - Budget For Medicinal Drugs With Predefined Details.png."
	else:
    		print "Unable to get the screenshot."
	QMessageBox.information( self.iface.mainWindow(),"Info", "Saved at /home/Floogin - Budget For Medicinal Drugs With Pre-defined Details.png")


    def screenshotBudget2(self):
	w = gtk.gdk.get_default_root_window()
	sz = w.get_size()
	print "The size of the window is %d x %d" % sz
	pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
	pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
	if (pb != None):
    		pb.save("Floogin - Budget For Medicinal Drugs With User-defined Details.png","png")
    		print "Screenshot saved to Floogin - Budget For Medicinal Drugs With User-defined Details.png."
	else:
    		print "Unable to get the screenshot."
	QMessageBox.information( self.iface.mainWindow(),"Info", "Saved at /home/Floogin - Budget For Medicinal Drugs With User-defined Details.png")


    def testChart (self) :
	frac = [25, 33, 17, 10, 15]
	labels = ['25', '33', '17', '10', '15']
	explode = [0, 0.25, 0, 0, 0]

	# Create pie chart
	pie(frac, explode, labels, shadow=True)
	# Give it a title
	title('A Sample Pie Chart')
	# save the plot to a PDF file rather than
	# display on screen
	savefig('pichart.pdf', dpi=200, format='PDF')


    def graphDiseases (self):
	
	ageChild = 0
	ageAdult = 0
	ageChildPercent = 0
	ageAdultPercent = 0
	percentLep = self.dlg.ui.cmbGraphLep.currentText()

	ageChildMis = 0
	ageAdultMis = 0
	ageChildPercentMis = 0
	ageAdultPercentMis = 0
	percentMis = self.dlg.ui.cmbGraphMeas.currentText()

	ageChildARI = 0
	ageAdultARI = 0
	ageChildPercentARI = 0
	ageAdultPercentARI = 0
	percentARI = self.dlg.ui.cmbGraphARI.currentText()

	popFloodLayer = self.iface.activeLayer()
	if self.dlg.ui.chkGraphLep.isChecked():
	   for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChild = ageChild + child
			ageChildPercent = float(ageChild) * float(percentLep)

			adult = feature['AGE_O_18']
			ageAdult = ageAdult + adult
			ageAdultPercent = float(ageAdult) * float(percentLep)

			totLep = ageChildPercent + ageAdultPercent

	
	if self.dlg.ui.chkGraphMeas.isChecked():
	   for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChildMis = ageChildMis + child
			ageChildPercentMis = float(ageChildMis) * float(percentMis)

			adult = feature['AGE_O_18']
			ageAdultMis = ageAdult + adult
			ageAdultPercentMis = float(ageAdultMis) * float(percentMis)

			totMis = ageChildPercentMis + ageAdultPercentMis

	if self.dlg.ui.chkGraphARI.isChecked():
	   for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChildARI = ageChildARI + child
			ageChildPercentARI = float(ageChildARI) * float(percentARI)

			adult = feature['AGE_O_18']
			ageAdultARI = ageAdultARI + adult
			ageAdultPercentARI = float(ageAdultARI) * float(percentARI)

			totARI = ageChildPercentARI + ageAdultPercentARI
	
	

	

	frac = [float(totLep), float(totMis),float(totARI)]
	labels = ['Leptospirosis', 'Measles', 'ARI']
	explode = [0, 0.25, 0]	

	#frac1 = [25, 33, 17, 10, 15]
	#labels1 = ['25', '33', '17', '10', '15']
	#explode1 = [0, 0.25, 0, 0, 0]

	# Create pie chart
	pie(frac, explode, labels, shadow=False) #
	# Give it a title
	title('Analyzing Diseases - Affetedt by flood - FLOOgin Report')
	# save the plot to a PDF file rather than
	# display on screen
	savefig('Analizing Diseases - FLOOgin Report.pdf', dpi=200, format='PDF')
	QMessageBox.information( self.iface.mainWindow(),"Info", "Saved at /home/Analizing Diseases - FLOOgin Report.pdf")

	

    
    

 #charts


    ############## start drug ##################  


    def loadGNAreas(self):
		try:
			
			stopHosp = self.dlg.ui.cmbHospitalLayerG.currentText()
			if stopHosp != 'Select layer': 
				global stopHospLayer
				stopHospLayer = self.getLayerByName( stopHosp )
				global fieldNameHosp
				fieldNameHosp = self.getFieldNameG(stopHospLayer)
				buildType = self.getFieldHosType(stopHospLayer)
				self.dlg.ui.cmbHospitalG.clear() 
				for feature in stopHospLayer.getFeatures():
					Type = feature[buildType]
					if Type == 'hospital':					
						name = feature[fieldNameHosp]
						if str(name) != 'NULL':
							self.dlg.ui.cmbHospitalG.addItem(str(name))
			
		except:
			e = sys.exc_info()[0]
			print e


    def loadHosToBudget(self):
	#if (state==Qt.Checked):
            for feature in self.cLayer.getFeatures():
			gnName = self.getFieldHosG(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'hospital':
				fid=feature.id()
				point = geom.asPoint()
				print point
				
				
				dsName = self.getFieldDSHos(self.cLayer)
				WdsName = feature[dsName]
								
				if str(WdsName) != 'NULL':
				  self.dlg.ui.cmbHospDS.addItem(str(WdsName))


    def drugsDistributionGN(self):
	selectedHos = self.dlg.ui.cmbHospDS.currentText()
	for feature in self.cLayer.getFeatures():
			gnName = self.getFieldHosG(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'hospital':
				fid=feature.id()
				point = geom.asPoint()
				print point

				gnName = self.getFieldGNDHos(self.cLayer)
				WgnName = feature[gnName]

				dsName = self.getFieldDSHos(self.cLayer)
				WdsName = feature[dsName]

				gnCodeName = self.getFieldGNDSubHos(self.cLayer)
				WgnCodeName = feature[gnCodeName]
			
	
				if selectedHos == str(WdsName): 
			 	 if str(WgnName) != 'NULL':
				   self.dlg.ui.cmbHospGN.addItem(str(WgnName))

				if selectedHos == str(WgnName): 
			 	 if str(WgnCodeName) != 'NULL':
				   self.dlg.ui.cmbHospGNC.addItem(str(WgnName))

    

    def drugsDistributionGNC(self):
	selectedHos = self.dlg.ui.cmbHospGN.currentText()
	for feature in self.cLayer.getFeatures():
			gnName = self.getFieldHosG(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'hospital':
				fid=feature.id()
				point = geom.asPoint()
				print point

				gnName = self.getFieldGNDHos(self.cLayer)
				WgnName = feature[gnName]

			

				gnCodeName = self.getFieldGNDSubHos(self.cLayer)
				WgnCodeName = feature[gnCodeName]


				if selectedHos == str(WgnName): 
			 	 if str(WgnCodeName) != 'NULL':
					#self.dlg.ui.cmbHospGNC.addItem(str(WgnCodeName))
					self.dlg.ui.txtIDPPop.setText(str(WgnCodeName))

    def testgg(self):
	Ds = 0
	affDs = str(self.dlg.ui.cmbHospDS.currentText())

	popFloodLayer = self.iface.activeLayer()

	#if self.dlg.ui.chkAffcetedMeaslesMale.isChecked():
	for feature in popFloodLayer.getFeatures():
			gnName = self.getFieldHosG(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'hospital':
				dss = feature['DSD_N']
				beds = feature['Beds']
				if dss == affDs:
					Ds = Ds + beds

	countDs = str(Ds)
	self.dlg.ui.txtHosPop.setText(countDs)


    def idpalloBud(self):
	Ds = 0
	affDs = str(self.dlg.ui.cmbIDPCDS.currentText())

	popFloodLayer = self.iface.activeLayer()

	#if self.dlg.ui.chkAffcetedMeaslesMale.isChecked():
	for feature in popFloodLayer.getFeatures():
			gnName = self.getFieldIDPG(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'school' or 'place_of_worship' or 'temple':
				cap = feature['Capacity']
				dss = feature['DSD_N']
				#beds = feature['Beds']
				if dss == affDs:
				  Ds = Ds + cap

	self.dlg.ui.txtIDPPopVal.setText(str(Ds))

	countDs = str(Ds)
	self.dlg.ui.txtHosPop.setText(countDs)
	

    def leppp(self):
	male = 0
	female = 0
	gnn = 0
	affgn = str(self.dlg.ui.txtGND.text())

	popFloodLayer = self.iface.activeLayer()

	#if self.dlg.ui.chkAffcetedMeaslesMale.isChecked():
	for feature in popFloodLayer.getFeatures():
			#ProvinceType = self.getFieldLe(self.cLayer) 						
			#Type = feature['PROVINCE_N']
				geom = feature.geometry()
			#if Type == 'Western':
				gn = feature['GND_N']
				maleC = feature['Male']
				if affgn == gn:
					male = male + maleC

				femaleC = feature['female']
				if affgn == gn:
					female = female + femaleC


	countTot = male + female
	countT = int(countTot)
	self.dlg.ui.txtHosPop_2.setText(str(countT))	

    def viewHosAvailabilyty(self):


	

	bed = float(str(self.dlg.ui.txtHosPop.text()))
	patients = float(str(self.dlg.ui.txtHosPop_2.text()))

	hospitalDS = str(self.dlg.ui.cmbHospDS.currentText())

	if bed > patients:
		self.dlg.ui.lblSufficient.setVisible(True)

	if bed < patients:
		self.dlg.ui.lblNotSufficient.setVisible(True)
		dsHos = str(self.dlg.ui.cmbHospDS.currentText())


    def viewHosAvailabilyty1(self):

	#global bed
	#bed = 0

	#global patients
	#patients = 0 cmbHospDS

	self.dlg.ui.lblGNArea_2.setVisible(False)
	self.dlg.ui.lblGNArea.setVisible(False)
	self.dlg.ui.lblProvnStatus.setVisible(False)
	self.dlg.ui.lblGNFemale.setVisible(False)
	self.dlg.ui.lblGNMale.setVisible(False)


	self.dlg.ui.lblGNArea_4.setVisible(True)
	self.dlg.ui.lblGNArea_3.setVisible(True)
	self.dlg.ui.lblGNMale_2.setVisible(True)

	bed = float(str(self.dlg.ui.txtHosPop.text()))
	patients = float(str(self.dlg.ui.txtHosPop_2.text()))

	hospitalDS = str(self.dlg.ui.cmbHospDS.currentText())

	if bed > patients:
		self.dlg.ui.lblSufficient.setVisible(True)

	if bed < patients:
		self.dlg.ui.lblNotSufficient.setVisible(True)
		dsHos = str(self.dlg.ui.cmbHospDS.currentText())

		#popFloodLayer = self.iface.activeLayer()
		for feature in self.cLayer.getFeatures():
			gnName = self.getFieldHosG(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'hospital':
				dsName = self.getFieldDSHos(self.cLayer)
				WdsName = feature[dsName]
		
				hosName = self.getFieldHosName(self.cLayer)
				WdshosName = feature[hosName]

				hosCap = self.getFieldHosBeds(self.cLayer)
				WdshosCap = feature[hosCap]	

				hosAdd = self.getFieldHosAddr(self.cLayer)
				WdshosAdd = feature[hosAdd]

				if str(WdsName) != hospitalDS :
				  	

					self.dlg.listAnalyzeDetails('<tr><td width="210">' + str(WdshosName) + '</td><td width="240">' + str(WdshosAdd) + '</td><td width="50">' + str(WdshosCap) + '</td></tr>')

					#self.dlg.listAnalyzeDetails('<tr><td width="250">' + str(WdshosAdd) + '</td></tr>')
	


    def nuOfBeds(self): 
	DSWise = 0
	GNWise = 0
	GNCWise = 0
	#affecGN = str(self.dlg.ui.txtOutBreak.text())
	affectDS = str(self.dlg.ui.cmbHospDS.currentText())
	affectGN = str(self.dlg.ui.cmbHospGN.currentText())
	affectGNC = str(self.dlg.ui.cmbHospGNC.currentText())
	
	for feature in self.cLayer.getFeatures():
			gnName = self.getFieldHosG(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'hospital':
				gnName = self.getFieldBedBud(self.cLayer)
				beds = feature['Beds']
				popFloodLayer = self.iface.activeLayer()

				#if self.dlg.ui.chkAffcetedMeaslesMale.isChecked():
				for feature in popFloodLayer.getFeatures():
					ds = feature['DSD_N']
					#gn = feature['GND_N']
					#gnc = feature['GND_C']
					if ds == affectDS :
                                          if str(beds) != 'NULL':
					        beds = feature['Beds']
					#if str(beds) != 'NULL':
					 #and gn == affectGN and gnc == affectGNC:
						DSWise = DSWise + int(beds)

	

	
	countDs = str(DSWise)
	self.dlg.ui.txtHosPop.setText(countDs)	

	


    def stopIDPIndexChangedBugdet(self):
		try:
			stopIDP = self.dlg.ui.cmbIDPCampLayerG.currentText()
			if stopIDP != 'Select layer': 
				global stopIDPLayer 
				stopIDPLayer = self.getLayerByName( stopIDP )
				global fieldNameIDP 
				fieldNameIDP = self.getFieldNameG(stopIDPLayer)
				buildType = self.getFieldIDPType(stopIDPLayer)
				self.dlg.ui.cmbIDPCampG.clear() 
				for feature in stopIDPLayer.getFeatures(): 						
					Type = feature[buildType]
					if Type == 'school' or Type == 'place_of_worship' or Type =='temple':
						name = feature[fieldNameIDP]
						if str(name) != 'NULL':
							self.dlg.ui.cmbIDPCampG.addItem(str(name))
			
		except:
			e = sys.exc_info()[0]
			print e


    def getFieldNameG(self, layer):
		try:
			fields = layer.pendingFields()
			fCount = fields.count()
			d = 0
			fieldName = ''
			while d < fCount:
				colHead = str(fields.field(d).name())
				colHeadLower = colHead.lower()
				for c in string.punctuation:
					colHeadLower= colHeadLower.replace(c," ")
				term = "name"
				words = colHeadLower.split()
				if term in words:
					fieldName = colHead
				d = d + 1
			if fieldName == '':
				fieldName = str(fields.field(0).name())
			return fieldName
		except:
			e = sys.exc_info()[0]
			print e

    def getFieldLepProvenArea(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldLepProvn = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldLepProvn = colHead
			d = d + 1
		if fieldLepProvn == '':
			fieldLepProvn = str(fields.field(21).name())
		return fieldLepProvn

    def getFieldGND(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldGN = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldGN = colHead
			d = d + 1
		if fieldGN == '':
			fieldGN = str(fields.field(6).name())
		return fieldGN

    def getFieldGNDIDP(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldGNI = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "GND_N"
			words = colHeadLower.split()
			if term in words:
				fieldGNI = colHead
			d = d + 1
		if fieldGNI == '':
			fieldGNI = str(fields.field(13).name())
		return fieldGNI


    def getFieldGNDHos(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldGN = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "GND_N"
			words = colHeadLower.split()
			if term in words:
				fieldGN = colHead
			d = d + 1
		if fieldGN == '':
			fieldGN = str(fields.field(13).name())
		return fieldGN

    def getFieldGNDSubHos(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldGN = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "GND_C"
			words = colHeadLower.split()
			if term in words:
				fieldGN = colHead
			d = d + 1
		if fieldGN == '':
			fieldGN = str(fields.field(14).name())
		return fieldGN

    def getFieldDSHos(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldGN = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "DSD_N"
			words = colHeadLower.split()
			if term in words:
				fieldGN = colHead
			d = d + 1
		if fieldGN == '':
			fieldGN = str(fields.field(12).name())
		return fieldGN


    def getFieldBedBud(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldGN = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "Beds"
			words = colHeadLower.split()
			if term in words:
				fieldGN = colHead
			d = d + 1
		if fieldGN == '':
			fieldGN = str(fields.field(4).name())
		return fieldGN


    def getFieldMale(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldMale = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldMale = colHead
			d = d + 1
		if fieldMale == '':
			fieldMale = str(fields.field(13).name())
		return fieldMale

    def getFieldFeMale(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldFMale = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldFMale = colHead
			d = d + 1
		if fieldFMale == '':
			fieldFMale = str(fields.field(14).name())
		return fieldFMale

    def affectedCategories(self):
        self.cLayer = self.canvas.currentLayer()  
        for feature in self.cLayer.getFeatures():
			lep = self.getFieldLepProvenArea(self.cLayer) 						
			Type = feature['LepProven']
			geom = feature.geometry()
			affecGND = str(self.dlg.ui.txtGND.text())
			lepArea = self.getFieldGND(self.cLayer)
			WLep = feature[lepArea] 
			LepW = str(WLep)	
			
			if Type == '1' and lepArea == 'LepW' :
			#if Type == 'Ingiriya' or Type == 'Diyagama' or Type == 'Imagira':
				#self.dlg.ui.label_67.setVisible(True) label_66
				self.dlg.ui.lblLepHos.setVisible(True)
				#self.dlg.ui.lblMostProvenLep.setVisible(True)
				#self.dlg.ui.lblCommProven.setVisible(True)
				fid=feature.id()
				point = geom.asPoint()
				print point
				global mGNDLoc
		       		mGNDLoc = QgsVertexMarker(self.canvas)
				
		       		
				name = self.getFieldGND(self.cLayer)
				WType = feature['GND_N']
				WName = feature[name]
				a=str(WType)
				b=str(WName)
				
				self.dlg.listAnalyzeDetails('<tr><td width="250">' + b + '</td><td></td><td width="160">' + a + '</td></tr>')	
				drug1Report.append( [str(WType), str(WName) ] )	
				
	
			else:
				#self.dlg.listAnalyzeDetails('<tr><td width="250">' + 'No' + '</td><td></td><td width="160">' + 'No' + '</td></tr>')			
				#QMessageBox.information( self.iface.mainWindow(),"Info", "Not checked" )
				caps = self.cLayer.dataProvider().capabilities()
				




    def getFieldDSPop(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldGN = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "DSD_N"
			words = colHeadLower.split()
			if term in words:
				fieldGN = colHead
			d = d + 1
		if fieldGN == '':
			fieldGN = str(fields.field(4).name())
		return fieldGN

    def getFieldDSPopIDP(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldDSI = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "DSD_N"
			words = colHeadLower.split()
			if term in words:
				fieldDSI = colHead
			d = d + 1
		if fieldDSI == '':
			fieldDSI = str(fields.field(12).name())
		return fieldDSI


    def selectAffecGNAreas(self,state): 

	self.dlg.ui.lblGNArea.setVisible(True)
	self.dlg.ui.lblProvnStatus.setVisible(True)
	self.dlg.ui.lblGNFemale.setVisible(True)
	self.dlg.ui.lblGNMale.setVisible(True)
	self.dlg.ui.lblGNArea_2.setVisible(True)

	
	style = getSampleStyleSheet() 
	pdf = SimpleDocTemplate("Affected GN Areas Details - FLOOgin Report.pdf")
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h1>'
	detailsWS.append( h2 + clR + "<b>Affected GN Areas Details - FLOOgin Report </b>" + clRs + h2s )
	
	global WatesSourcesLyrForRpt

	global storyWSRep
	storyWSRep = []
	global wsReport
	wsReport =[]
	global detailsWS
	detailsWS = []

	crs = str(self.iface.activeLayer().crs().authid())
	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")
	time = now.strftime("%H:%M")

	detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " 
	detDateTime = "Generated on : " + date + " at " + time
	detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
	detailsWS.append(str(detHazard))
	detailsWS.append(str(detDateTime))
	detailsWS.append(str(detCrs))

	global WSourceReport
	WSourceReport = []
        self.cLayer = self.canvas.currentLayer()  
	tb='<table style="width:500px"><tr><th width="200" align="left">GN Area Name</th><th></th><th width="200" align="left">Leptospirosis Most Proven Area </th></tr>'
	WSourceReport.append( ['GN Area Name', 'Leptospirosis Most Proven Area'] )
	styles = getSampleStyleSheet()
	nm = Paragraph('''<b>GN Area Name</b>''',styles["Normal"])
	tp = Paragraph('''<b>Leptospirosis Most Proven Area</b>''',styles["Normal"])
	wsReport.append( [ nm, tp] )
	self.dlg.listPopDetailWaterSource(tb) 
        if (state==Qt.Checked):
            for feature in self.cLayer.getFeatures():
			#ProvinceType = self.getFieldLe(self.cLayer) 						
			#Type = feature['PROVINCE_N']
				geom = feature.geometry()
			#if Type == 'Western':
				fid=feature.id()
				point = geom.asPoint()
				print point
				global mWSLoc
		       		mLepLoc = QgsVertexMarker(self.canvas)
		       		mLepLoc.setCenter(point)
		       		mLepLoc.setColor(QColor(255,0,0))
		       		mLepLoc.setIconSize(6)
                       		mLepLoc.setIconType(QgsVertexMarker.ICON_BOX)
                       		mLepLoc.setPenWidth(5)

				name = self.getFieldGND(self.cLayer)
				WName = feature[name]
				status = self.getFieldLepProvenArea(self.cLayer)
				WStatus = feature[status]
				female = self.getFieldFeMale(self.cLayer)
				Wfemale = feature[female]
				male = self.getFieldMale(self.cLayer)
				Wmale = feature[male]
				DS = self.getFieldDSPop(self.cLayer)
				DSDiv = feature[DS]

				ds = str(DSDiv)
				a=str(WStatus)
				b=str(WName)
				c=str(float(Wfemale))
				d=str(float(Wmale))
				self.dlg.listAnalyzeDetails('<tr><td width="120">' + ds + '</td><td width="100">' + b + '</td><td></td><td width="110">' + a + '</td><td width="95">' + c + '</td><td width="95">' + d + '</td></tr>')	
				WSourceReport.append( [str(WName), str(WStatus) ] )	

				wsReport.append( [str(WName), str(WStatus) ] )

				tbWS = Table(wsReport)
				storyWSRep.append( tbWS ) 
				pdf.build(storyWSRep)			
				
	
			#else:
				
				#caps = self.cLayer.dataProvider().capabilities()
				
	    print "test"

    def LoadAllIDP(self,state): 

	
	
	style = getSampleStyleSheet() 
	pdf = SimpleDocTemplate("Affected GN Areas Details - FLOOgin Report.pdf")
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h1>'
	detailsWS.append( h2 + clR + "<b>Affected GN Areas Details - FLOOgin Report </b>" + clRs + h2s )
	
	global WatesSourcesLyrForRpt

	global storyWSRep
	storyWSRep = []
	global wsReport
	wsReport =[]
	global detailsWS
	detailsWS = []

	crs = str(self.iface.activeLayer().crs().authid())
	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")
	time = now.strftime("%H:%M")

	detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " 
	detDateTime = "Generated on : " + date + " at " + time
	detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
	detailsWS.append(str(detHazard))
	detailsWS.append(str(detDateTime))
	detailsWS.append(str(detCrs))

	global WSourceReport
	WSourceReport = []
        self.cLayer = self.canvas.currentLayer()  
	
	WSourceReport.append( ['GN Area Name', 'Leptospirosis Most Proven Area'] )
	styles = getSampleStyleSheet()
	nm = Paragraph('''<b>GN Area Name</b>''',styles["Normal"])
	tp = Paragraph('''<b>Leptospirosis Most Proven Area</b>''',styles["Normal"])
	wsReport.append( [ nm, tp] )
	#self.dlg.listPopDetailfillBAE(tb) 
        if (state==Qt.Checked):
        	for feature in self.cLayer.getFeatures():
			#ProvinceType = self.getFieldLe(self.cLayer) 						
			#Type = feature['PROVINCE_N']
				geom = feature.geometry()
			#if Type == 'Western':
				fid=feature.id()
				point = geom.asPoint()
				print point
				global mWSLoc
		       		mLepLoc = QgsVertexMarker(self.canvas)
		       		mLepLoc.setCenter(point)
		       		mLepLoc.setColor(QColor(255,0,0))
		       		mLepLoc.setIconSize(6)
                       		mLepLoc.setIconType(QgsVertexMarker.ICON_BOX)
                       		mLepLoc.setPenWidth(5)

				name = self.getFieldGNDIDP(self.cLayer)
				WName = feature[name]
				status = self.getFieldIDPG(self.cLayer)
				WStatus = feature[status]
				capac = self.getFieldIDPcapBug(self.cLayer)
				Wcapac = feature[capac]
				DS = self.getFieldDSPopIDP(self.cLayer)
				DSDiv = feature[DS]

				ds = str(DSDiv)
				a=str(WName)
				b=str(Wcapac)
				c=str(status)
				
					

				if str(DSDiv) != 'NULL':
				  self.dlg.ui.cmbIDPCDS.addItem(str(DSDiv))

				
				

				WSourceReport.append( [str(DSDiv), str(WName) , str(WStatus) , str(Wcapac) ] )	

				wsReport.append( [str(DSDiv), str(WName) , str(WStatus) , str(Wcapac) ] )

				tbWS = Table(wsReport)
				storyWSRep.append( tbWS ) 
				pdf.build(storyWSRep)			
				
	
			#else:
				
				#caps = self.cLayer.dataProvider().capabilities()
				
	    #print "test"

    def drugsDistributionGNIDP(self):
	selectedHos = self.dlg.ui.cmbIDPCDS.currentText()
	for feature in self.cLayer.getFeatures():
			gnName = self.getFieldHosG(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'hospital' or 'place_of_worship' or 'temple':
				fid=feature.id()
				point = geom.asPoint()
				print point

				gnName = self.getFieldGNDIDP(self.cLayer)
				WgnName = feature[gnName]

				dsName = self.getFieldDSPopIDP(self.cLayer)
				WdsName = feature[dsName]


				if selectedHos == str(WgnName): 
			 	 if str(WgnCodeName) != 'NULL':
				   self.dlg.ui.cmbHospGNC.addItem(str(WgnName))


    def disRangeLepHosIndexChanged(self):
	global rangeLep	
	rlep = int(str(self.dlg.ui.cboDisRangeLepHos.currentText()))
	rlep = rlep * 1000
	if rlep == 1000:
		rangeLep = 1000
	elif rlep == 2000:
		rangeLep = 2000
	elif rlep == 3000:
		rangeLep = 3000
	elif rlep == 5000:
		rangeLep = 5000
	elif rlep == 8000:
		rangeLep = 8000
	elif rlep == 10000:
		rangeLep = 10000
	else:
		rangeLep = 2000



    def findNearbyHospForLep(self):
	global rangeLep
	point = []
	global rbLepAll
	rbLepAll = []
	vl = self.canvas.currentLayer()
	director = QgsLineVectorLayerDirector( vl, -1, '','', '', 3 )
	properter = QgsDistanceArcProperter()
	director.addProperter( properter )
	crs = self.canvas.mapRenderer().destinationCrs()
	builder = QgsGraphBuilder( crs )
	global xWellDetails
	global yWellDetails
	global rbpL	
	pStart = QgsPoint( xWellDetails, yWellDetails )
	
	delta = self.canvas.getCoordinateTransform().mapUnitsPerPixel() * 1
	rbp = QgsRubberBand( self.canvas)
	rbp.setColor( Qt.blue )
	rbp.addPoint( QgsPoint( pStart.x() - delta, pStart.y() - delta))
	rbp.addPoint( QgsPoint( pStart.x() + delta, pStart.y() - delta))
	rbp.addPoint( QgsPoint( pStart.x() + delta, pStart.y() + delta))
	rbp.addPoint( QgsPoint( pStart.x() - delta, pStart.y() + delta))
	
	tiedPoints = director.makeGraph( builder, [ pStart ] )
	graph = builder.graph()
	tStart = tiedPoints[ 0 ]
	idStart = graph.findVertex( tStart )
	( tree, cost ) = QgsGraphAnalyzer.dijkstra( graph, idStart, 0 )
	upperBound = []
	r = rangeLep
	i = 0
	while i < len(cost):
		if cost[ i ] > r and tree[ i ] != -1:
			outVertexId = graph.arc( tree [ i ] ).outVertex()
			if cost[ outVertexId ] < r:
				upperBound.append( i )
		i = i + 1
	co = 0	
	for i in upperBound:
		centerPoint = graph.vertex( i ).point()
		
		co = co + 1
		point.append(centerPoint)
		global rbLep
		rbLep = "rub " + str(co)
		rbLep = QgsRubberBand( self.canvas, True )
		rbLep.setColor( Qt.red )
		
        	rbLep.setWidth(10)
		rbLep.addPoint( QgsPoint( centerPoint.x() - delta, centerPoint.y()-delta))
		rbLep.addPoint( QgsPoint( centerPoint.x() + delta, centerPoint.y()-delta))
		rbLep.addPoint( QgsPoint( centerPoint.x() + delta, centerPoint.y()+delta))
		rbLep.addPoint( QgsPoint( centerPoint.x() - delta, centerPoint.y()+delta))
		rbLepAll.append(rbLep)
	
	j = 0
	while j < co-1:
		x1 = point[j]
		x2 = point[j + 1]
		j = j + 1
		
		point1 = QgsPoint(x1)
		
		point2 = QgsPoint(x2)
		
		global r
		r = QgsRubberBand(self.canvas, False) 
		points = [ point1,pStart ]
		r.setToGeometry(QgsGeometry.fromPolyline(points), None)

	global lyrTempLineLep
	lyrTempLineLep = 'line'
	layer = QgsVectorLayer('LineString?crs=epsg:4326','line',"memory")
	pr = layer.dataProvider()
	line = QgsFeature()		
	line.setGeometry(QgsGeometry.fromPolyline([point[co-1],point[0]]))
	pr.addFeatures([line])
	layer.updateExtents()
	QgsMapLayerRegistry.instance().addMapLayers([layer])

	

    def selectHosLepLoc(self):
	print "come"
	self.labelPos.clear()
	global stopPlace
	stopPlace = 1	
	self.place()
     
      	QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownIDPLoc)
            
        QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownIDPName)

	    
    def getFieldLe(self, layer): 
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldLe = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "PROVINCE_N"
			words = colHeadLower.split()
			if term in words:
				fieldLe = colHead
			d = d + 1
		if fieldLe == '':
			fieldLe = str(fields.field(0).name())
		return fieldLe

    def getFieldHosG(self, layer): 
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldLe = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldLe = colHead
			d = d + 1
		if fieldLe == '':
			fieldLe = str(fields.field(3).name())
		return fieldLe

    


    def getFieldIDPG(self, layer): 
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldLe = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldLe = colHead
			d = d + 1
		if fieldLe == '':
			fieldLe = str(fields.field(3).name())
		return fieldLe


    def getFieldIDPcapBug(self, layer): 
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldCa = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "Capacity"
			words = colHeadLower.split()
			if term in words:
				fieldCa = colHead
			d = d + 1
		if fieldCa == '':
			fieldCa = str(fields.field(21).name())
		return fieldCa



    def getFieldHosBeds(self, layer): 
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldLe = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "Beds"
			words = colHeadLower.split()
			if term in words:
				fieldLe = colHead
			d = d + 1
		if fieldLe == '':
			fieldLe = str(fields.field(4).name())
		return fieldLe

    def getFieldHosName(self, layer): 
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldLeNm = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "name"
			words = colHeadLower.split()
			if term in words:
				fieldLeNm = colHead
			d = d + 1
		if fieldLeNm == '':
			fieldLeNm = str(fields.field(2).name())
		return fieldLeNm

    def getFieldHosAddr(self, layer): 
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldLeAdd = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "address"
			words = colHeadLower.split()
			if term in words:
				fieldLeNm = colHead
			d = d + 1
		if fieldLeAdd == '':
			fieldLeAdd = str(fields.field(7).name())
		return fieldLeAdd



    def showMessage11(self):
      ageChild = 0
      ageAdult = 0
	#ageInfant = 0
      countmale = 0
      countfemale = 0
      vaccinedCount = 0
      total = 0
	
      popFloodLayer = self.iface.activeLayer()

      for feature in self.cLayer.getFeatures():
			affecGND = self.dlg.ui.txtGND.text()
			lepType = self.getFieldLepProvenArea(self.cLayer) 						
			Type = feature['LepProven']
			geom = feature.geometry()
			lepArea = self.getFieldGND(self.cLayer)
			WArea = feature['GND_N']
			geom = feature.geometry()
			
			#lepArea = self.getFieldGND(self.cLayer)
			#if Type == 'Yes' and WArea == affecGND :
				#self.dlg.ui.lblLepHos.setVisible(True)
			idx = cLayer.getFieldLepProvenArea('affecGND')
			ageChild =  feature.attributes()[idx]			
			
			

			tb='<table style="width:500px"><tr><th width="250" align="left">Age Group</th><th></th><th width="160" align="left">Victm Count</th></tr>'
	
			self.dlg.initiatePopulationTxtBox(tb)
	
			self.dlg.listPopDetailfillOE('<tr><td width="250">' + 'child' + '</td><td></td><td width="160">' + str(ageChild) + '</td></tr>')


			



			
	
			
    
    def affectedCategoriestest(self):
	#if (state==Qt.Checked):
	    
            for feature in self.cLayer.getFeatures():
			affecGND = self.dlg.ui.txtGND.text()
			lepType = self.getFieldLepProvenArea(self.cLayer) 						
			Type = feature['LepProven']
			geom = feature.geometry()
			lepArea = self.getFieldGND(self.cLayer)
			WArea = feature['GND_N']
			geom = feature.geometry()
			
			#lepArea = self.getFieldGND(self.cLayer)
			if Type == 'Yes' and WArea == affecGND:
				self.dlg.ui.lblLepHos.setVisible(True)
						
			if Type == 'No' and WArea == affecGND:
				self.dlg.ui.lblLepHos_2.setVisible(True)
					#caps = self.cLayer.dataProvider().capabilities()
				
	    print "test"

    def refreshResultBud(self):
	self.dlg.ui.textBrowser_2.clear()
	self.dlg.ui.lblDrugTotaLast.clear()
	self.dlg.ui.lblRs.setVisible(False)

    def affectedCategoriestest2(self):
	#if (state==Qt.Checked):
	    
            for feature in self.cLayer.getFeatures():
			affecGND = self.dlg.ui.txtGND.text()
			lepType = self.getFieldLepProvenArea(self.cLayer) 						
			Type = feature['LepProven']
			geom = feature.geometry()
			lepArea = self.getFieldGND(self.cLayer)
			WArea = feature['GND_N']
			geom = feature.geometry()
			
			if Type == 'No' and WArea == affecGND:
				self.dlg.ui.lblLepHos_2.setVisible(True)
			else:
				
				caps = self.cLayer.dataProvider().capabilities()
				
	    print "test"

    def riskLepClear(self): #btnClearLep
	self.dlg.ui.lblLepHos.setVisible(False)
	self.dlg.ui.lblLepHos_2.setVisible(False)
	#self.dlg.ui.chkAffRiskyY.setCheckState(0) 
	#self.dlg.ui.chkAffRiskyN.setCheckState(0) 
	self.dlg.ui.txtGND.clear()
	self.dlg.ui.chkAffRiskyY.setCheckState(0)
	self.dlg.ui.chkAffGND.setCheckState(0)
	self.dlg.ui.txtIDPPop.clear() 
	self.dlg.ui.txtHosPop_2.clear()
	self.dlg.ui.txtHosPop.clear()
	self.dlg.ui.chkAffRiskyY_3.setCheckState(0)
	self.dlg.ui.chkAffRiskyY_2.setCheckState(0) 
	self.dlg.ui.lblNotSufficient.setVisible(False)
	self.dlg.ui.lblSufficient.setVisible(False)

    def refresrLepresults(self):
	self.dlg.ui.lblGNArea_4.setVisible(False)
	self.dlg.ui.lblGNArea_3.setVisible(False)

	self.dlg.ui.txtBrowseAnalyz1.clear()
	self.dlg.ui.lblGNArea_2.setVisible(False)
	self.dlg.ui.lblGNArea.setVisible(False)
	self.dlg.ui.lblProvnStatus.setVisible(False)
	self.dlg.ui.lblGNFemale.setVisible(False)
	self.dlg.ui.lblGNMale.setVisible(False)

	self.dlg.ui.lblGNArea_4.setVisible(False)
	self.dlg.ui.lblGNArea_3.setVisible(False)

	
	
##Risk Analyze		   
    
    
    def showMessageAnalyze3(self):
	ageChild = 0
	ageAdult = 0

	popFloodLayer = self.iface.activeLayer()
	if self.dlg.ui.chkAffcetedMeasles.isChecked():
		for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChild = ageChild + child
			
			
	
	if self.dlg.ui.chkAffcetedMeasles.isChecked():
		for feature in popFloodLayer.getFeatures():
			adult = feature['AGE_O_18']
			ageAdult = ageAdult + adult
			

	countAllPop = ageChild + ageAdult

	tb='<table style="width:500px"><tr><th width="250" align="left">Age Group</th><th></th><th width="160" align="left">Victm Count</th></tr>'
	
	self.dlg.listAnalyzeDetailsMeasles(tb)
	
	self.dlg.listAnalyzeDetailsMeasles('<tr><td width="250">' + 'Affected Population' + '</td><td></td><td width="160">' + str(countAllPop) + '</td></tr>')

	#self.dlg.listAnalyzeDetailsARI2('<tr><td width="200">' + 'Children' + '</td><td></td><td width="160">' + str(ageChild) + '</td></tr>')
	

    def showMessageAnalyze4(self):
	vaccinedCount = 0
	
	
	popFloodLayer = self.iface.activeLayer()
	if self.dlg.ui.chkImmunizedMes.isChecked():
		for feature in popFloodLayer.getFeatures():
			vaccined = feature['TP']
			vaccinedCount = vaccinedCount + vaccined


	tb='<table style="width:500px"><tr><th width="250" align="left">Age Group</th><th></th><th width="160" align="left">Victm Count</th></tr>'
	
	self.dlg.listAnalyzeDetailsMeasles(tb)
	
	self.dlg.listAnalyzeDetailsMeasles('<tr><td width="250">' + 'Immunized Population' + '</td><td></td><td width="160">' + str(vaccinedCount) + '</td></tr>')

	#self.dlg.listAnalyzeDetailsARI2('<tr><td width="200">' + 'Children' + '</td><td></td><td width="160">' + str(ageChild) + '</td></tr>')
	

    def immunizedProcess(self):
	vaccinedCount = 0
	
	
	popFloodLayer = self.iface.activeLayer()
	if self.dlg.ui.chkImmunizedMes.isChecked():
		for feature in popFloodLayer.getFeatures():
			vaccined = feature['TP']
			vaccinedCount = vaccinedCount + vaccined


	ageChild = 0
	ageAdult = 0
	countAllPop = 0
	propotion = 0

	popFloodLayer = self.iface.activeLayer()
	if self.dlg.ui.chkAffcetedMeasles.isChecked():
		for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChild = ageChild + child
			
			
	
	if self.dlg.ui.chkAffcetedMeasles.isChecked():
		for feature in popFloodLayer.getFeatures():
			adult = feature['AGE_O_18']
			ageAdult = ageAdult + adult
			

	countAllPop = ageChild + ageAdult

	propotion = ( countAllPop / vaccinedCount)
	nf=self.dlg.ui.txtOutBreak.text()
	immunOut = str(nf)

	#immunOut = str(str(self.dlg.ui.txtOutBreak.text()))
	immunOutNew = float(immunOut)
	if propotion > immunOutNew:
	#if propotion > 2:
		self.dlg.ui.lblMeaslImmun.setVisible(True)
		#QMessageBox.information( self.iface.mainWindow(),"Info")

	if propotion < immunOutNew:
		self.dlg.ui.lblMeaslImmunNormal.setVisible(True)


    def showMessage(self):
	ageChild = 0
	ageAdult = 0
	#ageInfant = 0
	countmale = 0
	countfemale = 0
	vaccinedCount = 0
	total = 0
	
	popFloodLayer = self.iface.activeLayer()
	
	
	if self.dlg.ui.chkUnderEighteenAff_2.isChecked():
			for feature in popFloodLayer.getFeatures():
			#for feature in popVictimsLayerG.getFeatures():
				child = feature['AGE_U_18']
				ageChild = ageChild + child

	
	if self.dlg.ui.chkOverEighteenAff_2.isChecked():
			#for feature in popVictimsLayerG.getFeatures():
			for feature in popFloodLayer.getFeatures():
				adult = feature['AGE_O_18']
				ageAdult = ageAdult + adult

	
	
	if self.dlg.ui.chkMaleAff_2.isChecked():
			for feature in popFloodLayer.getFeatures():
			#for feature in popVictimsLayerG.getFeatures():
				male = feature['MALE']
				countmale = countmale + male

	if self.dlg.ui.chkFeMaleAff.isChecked():
			for feature in popFloodLayer.getFeatures():
			#for feature in popVictimsLayerG.getFeatures():
				female = feature['FEMALE']
				countfemale = countfemale + female

	





	tb='<table style="width:500px"><tr><th width="250" align="left">Age Group</th><th></th><th width="160" align="left">Victm Count</th></tr>'
	
	self.dlg.initiatePopulationTxtBox(tb)
	
	self.dlg.listPopDetailfillOE('<tr><td width="250">' + 'Adult' + '</td><td></td><td width="160">' + str(int(ageAdult)) + '</td></tr>')

	self.dlg.listPopDetailfillUE('<tr><td width="250">' + 'Children' + '</td><td></td><td width="160">' + str(int(ageChild)) + '</td></tr>')

	self.dlg.listPopDetailfillME('<tr><td width="250">' + 'Male' + '</td><td></td><td width="160">' + str(int(countmale)) + '</td></tr>')

	self.dlg.listPopDetailfillFE('<tr><td width="250">' + 'Female' + '</td><td></td><td width="160">' + str(int(countfemale)) + '</td></tr>')

	

    def lepTotDS(self):

	countmale = 0
	countfemale = 0
	affecGN = str(self.dlg.ui.txtGND.text())

	popFloodLayer = self.iface.activeLayer()

	#if self.dlg.ui.chkAffcetedMeaslesMale.isChecked():
	for feature in popFloodLayer.getFeatures():
			gnName = self.getFieldHosG(self.cLayer) 						
			Type = feature['type']
			geom = feature.geometry()
			if Type == 'hospital':
				dss = feature['DSD_N']
				beds = feature['Beds']
				if dss == affDs:
					Ds = Ds + beds

	countDs = str(Ds)
	self.dlg.ui.txtHosPop.setText(countDs)	


	
	countmale = 0
	countfemale = 0
	vaccined = 0
	affecGN = str(self.dlg.ui.txtGND.text())
	
	popFloodLayer = self.iface.activeLayer()

	#if self.dlg.ui.chkAffcetedMeaslesMale.isChecked():
	for feature in popFloodLayer.getFeatures():
			male = feature['MALE']
			gn = feature['GND_N']
			if gn == affecGN:
				countmale = countmale + male

	#if self.dlg.ui.chkAffcetedMeaslesFemale.isChecked():
	for feature in popFloodLayer.getFeatures():
			female = feature['FEMALE']
			gn = feature['GND_N']
			if gn == affecGN:
				countfemale = countfemale + female

	countmaleS = str(countmale)
	countfemaleS = str(countfemale)

	totaffected = float(countmaleS) + float(countfemaleS)
	self.dlg.ui.txtOutBreak.setText(str(totaffected))

    def testg(self):
	countmale = 0
	countfemale = 0
	vaccined = 0
	affecGN = str(self.dlg.ui.txtOutBreak.text())
	
	popFloodLayer = self.iface.activeLayer()

	if self.dlg.ui.chkAffcetedMeaslesMale.isChecked():
		for feature in popFloodLayer.getFeatures():
			male = feature['MALE']
			gn = feature['GND_N']
			if gn == affecGN:
				countmale = countmale + male

	if self.dlg.ui.chkAffcetedMeaslesFemale.isChecked():
		for feature in popFloodLayer.getFeatures():
			female = feature['FEMALE']
			gn = feature['GND_N']
			if gn == affecGN:
				countfemale = countfemale + female

	if self.dlg.ui.chkImmunizedMes.isChecked():
		for feature in popFloodLayer.getFeatures():
			meas = feature['MeaslesImm']
			gn = feature['GND_N']
			if gn == affecGN:
				vaccined = vaccined + meas

	
	countmaleS = str(countmale)
	countfemaleS = str(countfemale)
	vaccinedS = str(vaccined)

	vacTotal = float(countmaleS) + float(countfemaleS) - float(vaccinedS)
	
	
	

	self.dlg.listAnalyzeDetailsMeasles('<tr><td width="250">' + 'Male' + '</td><td></td><td width="160">' + str(vacTotal) + '</td></tr>')


    def showMessageMeasles(self):
	countmale = 0
	countfemale = 0
	vaccinedCount = 0
	total = 0
	vaccined = 0
	
	popFloodLayer = self.iface.activeLayer()
	
	if self.dlg.ui.chkAffcetedMeaslesMale.isChecked():
		for feature in popFloodLayer.getFeatures():
			male = feature['MALE']
			countmale = countmale + male

	if self.dlg.ui.chkImmunizedMes.isChecked():
		for feature in popFloodLayer.getFeatures():
			meas = feature['MeaslesImm']
			vaccined = vaccined + meas

	if self.dlg.ui.chkAffcetedMeaslesFemale.isChecked():
		for feature in popFloodLayer.getFeatures():
			female = feature['FEMALE']
			countfemale = countfemale + female

	self.dlg.ui.txtOutBreak_4.setText(str(countmale))
	self.dlg.ui.txtOutBreak_3.setText(str(countfemale))
	self.dlg.ui.txtOutBreak_2.setText(str(vaccined))

	maleC = str(self.dlg.ui.txtOutBreak_4.text())
	maleF = str(self.dlg.ui.txtOutBreak_3.text())
	vacC = str(self.dlg.ui.txtOutBreak_2.text())
	

	valTot = float(maleC) + float(maleF)
	toBeVaccined = valTot - float(vacC)
	outBreakVisible = self.dlg.ui.txtOutBreak_5.setText(str(toBeVaccined))
	

	outBreak = str(self.dlg.ui.txtOutBreak.text())
	outBreakVal = float(outBreak)

	if toBeVaccined > outBreakVal:
		self.dlg.ui.lblMeaslImmun.setVisible(True)
		

	if toBeVaccined < outBreakVal:
		self.dlg.ui.lblMeaslImmunNormal.setVisible(True)

	


	





	tb='<table style="width:500px"><tr><th width="250" align="left">Age Group</th><th></th><th width="160" align="left">Victm Count</th></tr>'
	
	self.dlg.listAnalyzeDetailsMeasles(tb)
	
	self.dlg.listAnalyzeDetailsMeasles('<tr><td width="250">' + 'Male' + '</td><td></td><td width="160">' + str(int(countmale)) + '</td></tr>')

	self.dlg.listAnalyzeDetailsMeasles('<tr><td width="250">' + 'Female' + '</td><td></td><td width="160">' + str(int(countfemale)) + '</td></tr>')

	self.dlg.listAnalyzeDetailsMeasles('<tr><td width="250">' + 'Total Victims' + '</td><td></td><td width="160">' + str(int(valTot)) + '</td></tr>')	

	self.dlg.listAnalyzeDetailsMeasles('<tr><td width="250">' + 'Vaccined Count' + '</td><td></td><td width="160">' + str(int(vaccined)) + '</td></tr>')

	

	
    def showMessageMeaslesToVaccine(self):
	countmale = 0
	countfemale = 0
	vaccinedCount = 0
	total = 0
	vaccined = 0
	
	popFloodLayer = self.iface.activeLayer()
	
	if self.dlg.ui.chkAffcetedMeaslesMale.isChecked():
		for feature in popFloodLayer.getFeatures():
			male = feature['MALE']
			countmale = countmale + male

	if self.dlg.ui.chkImmunizedMes.isChecked():
		for feature in popFloodLayer.getFeatures():
			meas = feature['MeaslesImm']
			vaccined = vaccined + meas

	if self.dlg.ui.chkAffcetedMeaslesFemale.isChecked():
		for feature in popFloodLayer.getFeatures():
			female = feature['FEMALE']
			countfemale = countfemale + female

	self.dlg.ui.txtOutBreak_4.setText(str(countmale))
	self.dlg.ui.txtOutBreak_3.setText(str(countfemale))
	self.dlg.ui.txtOutBreak_2.setText(str(vaccined))

	maleC = str(self.dlg.ui.txtOutBreak_4.text())
	maleF = str(self.dlg.ui.txtOutBreak_3.text())
	vacC = str(self.dlg.ui.txtOutBreak_2.text())
	

	valTot = float(maleC) + float(maleF)
	toBeVaccined = valTot - float(vacC)
	outBreakVisible = self.dlg.ui.txtOutBreak_5.setText(str(toBeVaccined))
	

	outBreak = str(self.dlg.ui.txtOutBreak.text())
	outBreakVal = float(outBreak)

	if toBeVaccined > outBreakVal:
		self.dlg.ui.lblMeaslImmun.setVisible(True)
		

	if toBeVaccined < outBreakVal:
		self.dlg.ui.lblMeaslImmunNormal.setVisible(True)

		
	self.dlg.listAnalyzeDetailsMeasles('<tr><td width="250">' + 'Remaining Population to be vaccined' + '</td><td></td><td width="160">' + str(toBeVaccined) + '</td></tr>')


    def generateMapManuallyDrug(self):
	PopLayer = self.dlg.ui.cboDrugLayer.currentText()	
	global floodLayer
	global PopPath
	global fdPathPop
	floodLayer = self.dlg.ui.cboFloodLayerDrug.currentText()
	outputFile = self.dlg.ui.leOutputFileDrug.text()
	allLayersList = self.canvas.layers()
 	for getLayer in allLayersList:
		if str(getLayer.name()) == str(PopLayer):
			PopPath = str(getLayer.source())

		elif str(getLayer.name()) == str(floodLayer):
			fdPathPop = str(getLayer.source())
	
	floodVectorLayer = QgsVectorLayer(PopPath, "flood_layer", "ogr")
	popVectorLayer = QgsVectorLayer(fdPathPop, "population_layer", "ogr")

	output = os.path.splitext(PopPath)[0]
	output += '_'+outputFile+'.shp'

	#processing.runandload("qgis:difference", rdPath, fdPath, output)

	overlayAnalyzer = QgsOverlayAnalyzer()
	overlayAnalyzer.intersection(floodVectorLayer, popVectorLayer, output) 

	#processing.runandload("qgis:intersect" , WellPath, fdPathWell, output)
	#processing.runalg("qgis:difference", WellPath, fdPathWell, output)
	wb = QgsVectorLayer(output, outputFile, 'ogr')
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
	else:
		print "No layer found"

	#active new layer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		if str(getLayerNew.name()) == str(outputFile):
			legend.setLayerVisible(getLayerNew, True)
		elif str(getLayerNew.name()) == str(floodLayer):
			legend.setLayerVisible(getLayerNew, True)
		else: 
			legend.setLayerVisible(getLayerNew, False)


    def clearDrugEstimation(self):
	self.dlg.ui.cboDrugLayer.clear()
	self.dlg.ui.cboFloodLayerDrug.clear()
	self.dlg.ui.leOutputFileDrug.clear()

	allLayersIn = self.canvas.layers()
 	for LayerNow in allLayersIn:	
		self.dlg.ui.cboDrugLayer.addItem(LayerNow.name())
                self.dlg.ui.cboFloodLayerDrug.addItem(LayerNow.name())
	colRd = '<font color="red">'
	colRds = '</font>'
	self.dlg.ui.txtFirstStepsDrugs.clear()
	self.dlg.ui.txtFirstStepsDrugs.setText(colRd + "<b>Please follow these steps</b>" + colRds + '\n' + "<b>(Press on down arrow to start)</b>")
	global nWell
	nWell = 0
	global nowWell
	nowWell = 2

   
    def getFieldPopDrugType(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldPopType = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldPopType = colHead
			d = d + 1
		if fieldPopType == '':
			fieldPopType = str(fields.field(1).name())
		return fieldPopType

   


    def resetDrug(self, primary_keywords_only=True): 
        """Reset all controls to a blank state.

        :param primary_keywords_only: If True (the default), only reset
            Subcategory, datatype and units.
        :type primary_keywords_only: bool
        """

        
	self.dlg.ui.lblLayerNameIDP.clear()


    
    def stepsUpDrug(self): 
	stepz = self.genMapStepsDrug() 
	
	global nowPop
	nowPop = nowPop - 1
	global nPop
	nPop = nPop - 1
	if nowPop < 1:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[0])
		nPop = 1
	if nowPop == 1:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[0])
	if nowPop == 2:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[1])
	if nowPop == 3:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[2])
	if nowPop == 4:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[3])
	if nowPop == 5:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[4])
	if nowPop == 6:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[5])
	#if nowIDP == 7:
		#self.dlg.ui.txtFirstSteps.setText(stepz[5])

	
		

    def stepsDownDrug(self): 
	#one, two, three, four, five, six, seven = self.genMapSteps()
	#curStep = self.dlg.ui.txtFirstSteps.toHtml()
	stepz = self.genMapStepsDrug()
	global nowPop
	global nPop
	nPop = nPop + 1
	
	if nPop == 1:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[0])
		nowPop = 1
	if nPop == 2:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[1])
		nowPop = 2
	if nPop == 3:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[2])
		nowPop = 3
	if nPop == 4:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[3])
		nowPop = 4
	if nPop == 5:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[4])
		nowPop = 5
	if nPop == 6:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[5])
		nowPop = 6
	if nPop == 7:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[6])
		nowPop = 7
	if nPop > 7:
		self.dlg.ui.txtFirstStepsDrugs.setText(stepz[6])
		nowPop = 7

    
    def genMapStepsDrug(self): 
	steps = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>' 
	one = "<b>Step 1</b> : Load the " + clBl + "flood-hazard layer " + clBls + "and " + clBl + "Population layer " + clBls
	two = "<b>Step 2</b> : Check whether a file with " + clR + ".keywords " + clRs + "extension, is available in each layer bundle "
	three = "<b>Step 3</b> : If (.keywords files) available, press on " + clBl + "Generate map for process " + clBls + "button to generate a " + clBl + "flood-safe " + clBls + "layer "
	four = "<b>Step 4</b> : If (.keywords files) " + clR + "not " + clRs + "available, select the " + clBl + "flood-hazard layer " + clBls + "and " + clBl + "well layer " + clBls + "from the drop downs and provide a name for the output shapefile "
	five = "<b>Step 5</b> : " + clR + "(If followed step 4) " + clRs + "press on " + clBl + "Generate map " + clBls + "button to generate a " + clBl + "flood-safe " + clBls + "layer "
	six = "<b>Step 6</b> : The generated " + clBl + "flood-safe " + clBls + "layer will be automatically loaded to the TOC and will be saved in your " + clBl + "/home " + clBls + "directory "
	seven = clR + "<b><h3>Now you can start</h3></b> " + clRs  	

	self.dlg.ui.txtFirstStepsDrugs.clear()	
	steps.append(one)
	steps.append(two)
	steps.append(three)
	steps.append(four)
	steps.append(five)
	steps.append(six)
	steps.append(seven)
	
	#return one, two, three, four, five, six, seven
	return steps
#

    
    def genMapStepsBudget(self): 
	stepzz = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>' 
	one = clBl+"<h3>1. Select Main Disease Type and Diseases Belongs</h3>" + clBls
	two = clBl + "<h3>2. Enter OR Select Patient Count</h3>" + clBls
	three = clBl + "<h3>3. Then Go For Calculations</h3>" + clBls
	four = clR + "<h3>Now you can start</h3>" + clRs  	

	self.dlg.ui.txtFirstStepsDrugsBugget.clear()	
	stepzz.append(one)
	stepzz.append(two)
	stepzz.append(three)
	stepzz.append(four)
	
	#return one, two, three, four, five, six, seven
	return stepzz

    def stepsUpDrugBug(self): 
	stepzz = self.genMapStepsBudget() 
	global nowBug
	nowBug = nowBug - 1
	global nBug
	nBug = nBug - 1
	if nowBug < 1:
		self.dlg.ui.txtFirstStepsDrugsBugget.setText(stepzz[0])
		nBug = 1
	if nowBug == 1:
		self.dlg.ui.txtFirstStepsDrugsBugget.setText(stepzz[0])
	if nowBug == 2:
		self.dlg.ui.txtFirstStepsDrugsBugget.setText(stepzz[1])
	if nowBug == 3:
		self.dlg.ui.txtFirstStepsDrugsBugget.setText(stepzz[2])
	if nowBug == 4:
		self.dlg.ui.txtFirstStepsDrugsBugget.setText(stepzz[3])
	

	
		

    def stepsDownDrugBug(self): 
	#one, two, three, four, five, six, seven = self.genMapSteps()
	#curStep = self.dlg.ui.txtFirstSteps.toHtml()
	stepzz = self.genMapStepsBudget()
	global nowBug
	global nBug
	nBug = nBug + 1
	
	if nBug == 1:
		self.dlg.ui.txtFirstStepsDrugsBugget.setText(stepzz[0])
		nowBug = 1
	if nBug == 2:
		self.dlg.ui.txtFirstStepsDrugsBugget.setText(stepzz[1])
		nowBug = 2
	if nBug == 3:
		self.dlg.ui.txtFirstStepsDrugsBugget.setText(stepzz[2])
		nowBug = 3
	if nBug == 4:
		self.dlg.ui.txtFirstStepsDrugsBugget.setText(stepzz[3])
		nowBug = 4
	
    
    def calcDrugBugdet(self):
	drug_name_list=[]
	drug_price_list=[]
	drug_dose_list=[]
	categary_list=[]
	e="true"
	drug_name_index=0
	drug_price_index=0
	drug_dose_index=0
	total_price=0
	child_total_cost=0
	abult_total_cost=0

	while(e=="true"):
    
		
		input_drug_name = self.dlg.ui.lineEdit.text() 
		if(input_drug_name=="cal"):
		  e="false"
		  continue
		
		input_drug_price = str(self.dlg.ui.txtPrice.text())
		

		input_drug_dose = str(self.dlg.ui.cmbChild.currentText())

		
 
		drug_name_list.append(input_drug_name)
		drug_price_list.append(drug_price_index)
		drug_dose_list.append(input_drug_dose)
	print drug_name_list

	while(drug_name_index<len(drug_name_list)):
   		drugname = drug_name_list[drug_name_index]
   		price= drug_price_list[drug_name_index]
   		dose=drug_dose_list[drug_name_index]
   		print drugname
   		print price
   		print dose
   		
		if self.dlg.ui.chkDoseChild.isChecked():
      			child_cost=float(dose)*float(price)
      			print "your drug is ",drugname
      			print "your cost is ",child_cost
      			print "categary",categary
      			child_total_cost=child_total_cost+child_cost


   		if self.dlg.ui.chkDoseAdult.isChecked():
      			abult_cost=float(dose)*float(price)
      			print "your drug is ",drugname
      			print "your cost is ",abult_cost
      			print "categary",categary
      			abult_total_cost=abult_total_cost+abult_cost
  
  
   

		if(drug_name_index<len(drug_name_list)):
      			drug_name_index=drug_name_index+1

	total_price=child_total_cost+abult_total_cost
	print "total cost for child",child_total_cost
	print "total cost for abult",abult_total_cost
	print "your total cost",total_price

	QMessageBox.information( self.iface.mainWindow(),"Info", "%d"%total_price )

	

	tb='<table style="width:500px"><tr><th width="250" align="left">AAA</th><th></th><th width="160" align="left">BBB</th></tr>'
	
	self.dlg.initiatePopulationTxtBox(tb)
	
	self.dlg.listPopDetailfillBAE('<tr><td width="250">' + 'budget' + '</td><td></td><td width="160">' + str(total_price) + '</td></tr>')

	self.dlg.listPopDetailfillBAE('<tr><td width="250">' + 'Adult budget' + '</td><td></td><td width="160">' + str(abult_total_cost) + '</td></tr>')

	

	
    ################ End Medicinal Drugs ######################### 

    def countQtyD(self): # delete this function
	global totalQtyA
	totalQtyA = 0

	global totalQtyA
	totalQtyA = 0

	global totalQtyC
	totalQtyC = 0

	childPer= self.dlg.ui.cmbDChild.currentText()
	childPerVala = str(childPer)
	childPerVal = float(childPerVala)

	adultPer= self.dlg.ui.cmbDAdult.currentText()
	adultPerVala = str(adultPer)
	adultPerVal = float(adultPerVala)

	ageChild = 0
	ageAdult = 0
	popFloodLayer = self.iface.activeLayer()
	if self.dlg.ui.chkAdultCount.isChecked():
		for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChild = ageChild + child

	if self.dlg.ui.chkChildCount.isChecked():
		for feature in popFloodLayer.getFeatures():
			adult = feature['AGE_O_18']
			ageAdult = ageAdult + adult

	
	for x in range(0, len(doseAdultList)):
		qtyA =  doseAdultList[x]
		totalQtyA = (float(totalQtyA) + float(qtyA)) + ageAdult
		#disPrice = str(totalPrice)
	#self.dlg.ui.lblTotBudget.setText(totalPrice) str(doseAdultListG[x])

	for x in range(0, len(doseChildrenList)):
		qtyC =  doseChildrenList[x]
		totalQtyC = (float(totalQtyC) + float(qtyC)) + ageChild

	totalDrugQty = (totalQtyA  * (ageAdult * adultPerVal) ) + (totalQtyC * (ageChild * childPerVal) )
	#totalDrugQty = (totalQtyA  * adultPerVal ) + (totalQtyC * childPerVal )

	totalParacetamolCount = totalDrugQty / 500.0


	self.dlg.ui.lineEdit.setText(str(totalParacetamolCount))


    def generateReportBudget(self):
	style = getSampleStyleSheet()	
	pdf = SimpleDocTemplate("Alternative Route Finder-FLOOgin Report.pdf")
	story = []
	details = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h1>'
	
	detailsBudget.append( h2 + clR + "<b>Medicinal Drugs Estimation - FLOOgin Report </b>" + clRs + h2s )

	global startNameForReportBudget
	global stopNameForReportBudget
	
	crs = str(self.iface.activeLayer().crs().authid())

	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")
	time = now.strftime("%H:%M")

	detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " + clBl + str(floodLyrForRpt) + clBls
	detDateTime = "Generated on : " + date + " at " + time
	detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates" 
	detDrugsEstimation = clBl + "<b>Meddicinal Drugs Estimation</b> " + clBls
	detFrom = clBl + "From :- " + clBls + str(startNameForReportBudget)
	detFromCo = clBl + "Coordinates :- X : " + clBls + str(x1) + ", " + clBl + "Y : " + clBls + str(y1)  	
	detTo = clBl + "To :- " + clBls + str(stopNameForReportBudget)
	detToCo = clBl + "Coordinates :- X : " + clBls + str(x2) + ", " + clBl + "Y : " + clBls + str(y2)
	
	
	detailsBudget.append(str(detHazard))
	detailsBudget.append(str(detDateTime))
	detailsBudget.append(str(detCrs))
	detailsBudget.append(str(detDrugsEstimation))	
	detailsBudget.append(str(detFrom))
	
	details.append(str(detFromCo))
		
	details.append(str(detTo))
	
	details.append(str(detToCo))
	
	details.append(str(detDis))
	
	details.append(str(detDism))
	
	details.append(str(detModeTrans))
	details.append(str(detSpeed))
	details.append(str(detTime))
	details.append(str(detDirec))

    def countDrugTotal(self):
	

	global ageChild
	global ageAdult

	ageChildCC = self.dlg.ui.txtAdultCount.text()
	ageChild = str(ageChildCC)

	ageAdultAC = self.dlg.ui.txtChildCount.text()
	ageAdult = str(ageAdultAC)

	global percentChildC 
	percentChildC = float(self.dlg.ui.cmbChild.currentText())
	global percentAdultA
	percentAdultA = float(self.dlg.ui.cmbAdult.currentText()) 
	

	global totalPrice
	totalPrice = 0

	global totalQytA
	totalQytA = 0

	global totalQytC
	totalQytC = 0

	global totalQyt
	totalQyt = 0

	timesPerDay = self.dlg.ui.txtTimeDay.text()
	timesPerDayS = str(timesPerDay)

	nuOfDays = self.dlg.ui.txtDays.text()
	nuOfDaysS = str(nuOfDays)

	for x in range(0, len(drugPriceG)):
		price =  drugPriceG[x]
		totalPrice = float(totalPrice) + float(price)
		
	
	for x in range(0, len(drugChildQty)):
		qtyC =  drugChildQty[x]
		totalQytC = float(totalQytC) + float(qtyC)
		#self.dlg.ui.txtDoseC.setText(str(totalQytC))

	for x in range(0, len(drugAdultQty)):
		qtyA =  drugAdultQty[x]
		totalQytA = float(qtyA) + float(totalQytA)
		#self.dlg.ui.txtDoseA.setText(str(totalQytA))

	

	dname = self.dlg.ui.lineEdit.text()


	self.dlg.ui.lblTotBudget.setText('Total Budget value = '+ str(totalPrice)) #"%d"totalPrice
	


    def countDrug(self):

	drugReport.append(Image("a.png", 2*inch, 1*inch))
	#story.append(Image("mottoo.png", 4*inch, 0.5*inch))
	
	style = getSampleStyleSheet()	
	pdf = SimpleDocTemplate("Medicinal Drugs Estimation with - FLOOgin Report.pdf")
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h1>'
	detailsBudget.append( h2 + clR + "<b>Medicinal Drugs Estimation - FLOOgin Report </b>" + clRs + h2s )
	
	global floodLyrForBudRpt

	crs = str(self.iface.activeLayer().crs().authid())
	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")
	time = now.strftime("%H:%M")

	detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " #+ clBl + str(floodLyrForBudRpt) + clBls
	detDateTime = "Generated on : " + date + " at " + time
	detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
	detailsBudget.append(str(detHazard))
	detailsBudget.append(str(detDateTime))
	detailsBudget.append(str(detCrs))	

	drugname=self.dlg.ui.lineEdit.text() #nf
	dName = str(drugname)

	#global s txtPrice
	drugPrice1=self.dlg.ui.txtPrice.text() #sf
	dPrice = str(drugPrice1)

	childQtyC= self.dlg.ui.cmbChild.currentText() #cf
	cQtyC = str(childQtyC)

	adultQtyA= self.dlg.ui.cmbAdult.currentText() #af
	acQtyA = str(adultQtyA)

	timesPerDay = self.dlg.ui.txtTimeDay.text()
	timesPerDayS = str(timesPerDay)

	nuOfDays = self.dlg.ui.txtDays.text()
	nuOfDaysS = str(nuOfDays)


	global ageChild
	global ageAdult

	
	ageChildC = self.dlg.ui.txtAdultCount.text()
	ageChild = str(ageChildC)

	
	ageAdultA = self.dlg.ui.txtChildCount.text()
	ageAdult = str(ageAdultA)
	
	
	global drugReport
	drugReport =[]
	global detailsBudget
	detailsBudget = []
	
	


   	drugNameListG.append(dName)
   	drugPriceListG.append(dPrice)
   	doseChildrenListG.append(cQtyC)
   	doseAdultListG.append(acQtyA)
	priceForOne = (float(ageAdult) * float(dPrice) * float(acQtyA) * float(timesPerDayS)*float(nuOfDaysS)) + (float(ageChild) * float(dPrice) * float(cQtyC)* float(timesPerDayS)*float(nuOfDaysS))  
	drugPriceG.append(str(priceForOne))

	#qtyAsCapSize = float(str(self.dlg.ui.cmbDrugSize_2.currentText()))

	qtyForChild = ((float(ageChild) * float(cQtyC) * float(timesPerDayS) * float(nuOfDaysS) ) ) 
	qtyForAdult = ((float(ageAdult) * float(acQtyA) * float(timesPerDayS) * float(nuOfDaysS) ) ) 
	drugChildQty.append(str(qtyForChild))	
	drugAdultQty.append(str(qtyForAdult))	

	self.dlg.ui.textBrowser.clear()

	global drugQtySize1
	drugQtySize1 = str(self.dlg.ui.cmbDrugSize_2.currentText())
	#self.dlg.ui.txtdrugMan.setText(str(drugQtySize1))
	#a = self.dlg.ui.txtdrugMan.text()
	givCmb1.append(str(drugQtySize1))
	
	#tb='<table style="width:500px"><tr><th width="160" align="left">Name</th><th width="90" align="left">Unit_Price</th><th width="90" align="left">Child_Qty</th><th width="90" align="left">Adult_Qty</th><th width="90" align="left">Price</th><</tr>'
	tb='<table style="width:500px"><tr><th width="100" align="left">Name</th><th width="90" align="left">Size(mg/ml)</th><th width="90" align="left">Unit_Price</th><th width="90" align="left">Child_Qty</th><th width="90" align="left">Adult_Qty</th><th width="90" align="left">Price</th><</tr>'


	#self.dlg.listPopDetailfillBAE(tb)
	
	styles = getSampleStyleSheet()
	nm = Paragraph('''<b>NAME</b>''',styles["Normal"])
	tp = Paragraph('''<b>Unit Price</b>''',styles["Normal"])
	cs = Paragraph('''<b>Child Qty</b>''',styles["Normal"])
	md = Paragraph('''<b>Adult Qty</b>''',styles["Normal"])
	pd = Paragraph('''<b>Price</b>''',styles["Normal"])
	ccs = Paragraph('''<b>Capsual or Packet Size</b>''',styles["Normal"])
	drugReport.append( [ nm, tp, cs, md , pd , ccs ] )
	self.dlg.listPopDetailfillBAE(tb)
	for x in range(0, len(drugNameListG)):

		
		
		self.dlg.listPopDetailfillBAE('<tr><td width="100">'+str(drugNameListG[x])+'</td><td width="90">'+str(givCmb1[x])+'</td><td width="90">'+str(drugPriceListG[x])+'</td><td width="90">'+str(drugChildQty[x])+'</td><td width="90">'+str(drugAdultQty[x])+'</td><td width="90">'+str(drugPriceG[x])+'</td></tr>')
	   #drugReport.append( [str(drugNameListG[x]), str(drugPriceListG[x]), str(drugChildQty[x]), str(drugAdultQty[x]),str(drugPriceG[x]) ] )
		drugReport.append( [str(drugNameListG[x]), str(drugQtySize1) , str(drugPriceListG[x]), str(drugChildQty[x]), str(drugAdultQty[x]),str(drugPriceG[x]) ] )


		#self.dlg.ui.txtdrugMan.setText(str(drugNameListG[x]))
		#viewtot1 = str(self.dlg.ui.txtdrugMan.text())

		
		#if drugQtySize1 == '500':
				#qtyCalc = float(qtyCal1) / 500.0
				#qtyCalc = float(viewtot1) / 500.0
				#self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

		#if drugQtySize1 == '250':
				#qtyCalc = float(qtyCal1) / 250.0
				#qtyCalc = float(viewtot1) / 250.00
				#self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

		#if drugQtySize1 == '100':
				#qtyCalc = float(qtyCal1) / 100.0
				#qtyCalc = float(viewtot) / 100.00
				#self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

		#if drugQtySize1 == '25':
				#qtyCalc = float(qtyCal1) / 100.0
				#qtyCalc = float(viewtot1) / 25.00
				#self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

		#if drugQtySize1 == '50':
				#qtyCalc = float(qtyCal1) / 100.0
				#qtyCalc = float(viewtot1) / 50.00
				#self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

		#if drugQtySize1 == '750':
				#qtyCalc = float(qtyCal1) / 100.0
				#qtyCalc = float(viewtot1) / 750.00
				#self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

		#if drugQtySize1 == '1000':
				#qtyCalc = float(qtyCal1) / 100.0
				#qtyCalc = float(viewtot1) / 1000.00
				#self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))
			

		tbDrugEst = Table(drugReport)
		storyBudget.append( tbDrugEst ) 
		pdf.build(storyBudget)
	

	#self.viewSummary()
    def countDrugg(self):
	style = getSampleStyleSheet()	
	pdf = SimpleDocTemplate("Medicinal Drugs Estimation - FLOOgin Report.pdf")
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h1>'
	detailsBudget.append( h2 + clR + "<b>Medicinal Drugs Estimation - FLOOgin Report </b>" + clRs + h2s )
	
	global floodLyrForBudRpt

	crs = str(self.iface.activeLayer().crs().authid())
	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")
	time = now.strftime("%H:%M")

	detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " #+ clBl + str(floodLyrForBudRpt) + clBls
	detDateTime = "Generated on : " + date + " at " + time
	detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
	detailsBudget.append(str(detHazard))
	detailsBudget.append(str(detDateTime))
	detailsBudget.append(str(detCrs))

	
	
	nf=self.dlg.ui.lineEdit.text()
	n = str(nf)
	#global s txtPrice
	sf=self.dlg.ui.txtPrice.text()
	s = str(sf)
	cf= self.dlg.ui.cmbChild.currentText()
	c = str(cf)
	af= self.dlg.ui.cmbAdult.currentText()
	a = str(af)

	timesPerDay = self.dlg.ui.txtTimeDay.text()
	timesPerDayS = str(timesPerDay)

	nuOfDays = self.dlg.ui.txtDays.text()
	nuOfDaysS = str(nuOfDays)


	global ageChild
	global ageAdult

	
	ageChildC = self.dlg.ui.txtAdultCount.text()
	ageChild = str(ageChildC)

	
	ageAdultA = self.dlg.ui.txtChildCount.text()
	ageAdult = str(ageAdultA)
	
	global storyBudget
	storyBudget = []
	global drugReport
	drugReport =[]
	global detailsBudget
	detailsBudget = []
   	drugNameListG.append(n)
   	drugPriceListG.append(s)
   	doseChildrenListG.append(c)
   	doseAdultListG.append(a)
	priceForOne = (float(ageAdult) * float(s) * float(c) * float(timesPerDayS)*float(nuOfDaysS)) + (float(ageChild) * float(s) * float(a)* float(timesPerDayS)*float(nuOfDaysS))#((100 * float(s)) #* float(c) ) + (150 * float(s) * float(a) )
	drugPriceG.append(str(priceForOne))
	
	self.dlg.ui.textBrowser.clear()
	
	tb='<table style="width:500px"><tr><th width="70" align="left">Name</th><th width="70" align="left">Unit_Price</th><th width="70" align="left">Child_Qty</th><th width="70" align="left">Adult_Qty</th><th width="70" align="left">Price</th><</tr>'

	styles = getSampleStyleSheet()
	nm = Paragraph('''<b>NAME</b>''',styles["Normal"])
	tp = Paragraph('''<b>Unit Price</b>''',styles["Normal"])
	cs = Paragraph('''<b>Child Qty</b>''',styles["Normal"])
	md = Paragraph('''<b>Adult Qty</b>''',styles["Normal"])
	pd = Paragraph('''<b>Price</b>''',styles["Normal"])
	drugReport.append( [ nm, tp, cs, md , pd ] )
	self.dlg.listPopDetailfillBAE(tb)
	
	
	for x in range(0, len(drugNameListG)):
		
	   self.dlg.listPopDetailfillBAE('<tr><td width="70">'+str(drugNameListG[x])+'</td><td width="70">'+str(drugPriceListG[x])+'</td><td width="70">'+str(doseChildrenListG[x])+'</td><td width="70">'+str(doseAdultListG[x])+'</td><td width="70">'+str(drugPriceG[x])+'</td></tr>')
	   drugReport.append( [str(drugNameListG[x]), str(drugPriceListG[x]), str(doseChildrenListG[x]), str(doseAdultListG[x]),str(drugPriceG[x]) ] )

	tbDrugEst = Table(drugReport)
	storyBudget.append( tbDrugEst ) 
	pdf.build(storyBudget)

	#self.viewSummary()

    def viewSummary(self):

	global totalPrice
	totalPrice = 0

	global totalQytA
	totalQytA = 0

	global totalQytC
	totalQytC = 0

	global totalQyt
	totalQyt = 0

	
	global ageChildC
	global ageAdultA

	ageChildCC = self.dlg.ui.txtAdultCount.text()
	ageChildC = str(ageChildCC)

	ageAdultAC = self.dlg.ui.txtChildCount.text()
	ageAdultA = str(ageAdultAC)

	timesPerDay = self.dlg.ui.txtTimeDay.text()
	timesPerDayS = str(timesPerDay)

	nuOfDays = self.dlg.ui.txtDays.text()
	nuOfDaysS = str(nuOfDays)

	timesPerDay = self.dlg.ui.txtTimeDay.text()
	timesPerDayS = str(timesPerDay)

	nuOfDays = self.dlg.ui.txtDays.text()
	nuOfDaysS = str(nuOfDays)

	
	for x in range(0, len(drugPriceG)):
		price =  drugPriceG[x]
		totalPrice = float(totalPrice) + float(price)
		
	
	for x in range(0, len(drugChildQty)):
		qtyC =  drugChildQty[x]
		totalQytC = float(totalQytC) + float(qtyC)
		#self.dlg.ui.txtDoseC.setText(str(totalQytC))

	for x in range(0, len(drugAdultQty)):
		qtyA =  drugAdultQty[x]
		totalQytA = float(qtyA) + float(totalQytA)


	self.dlg.ui.txtDoseA.setText(str(doseAdultListG[x]))
	self.dlg.ui.txtDoseC.setText(str(doseChildrenListG[x]))
	totA = self.dlg.ui.txtDoseA.text() 
	totC = self.dlg.ui.txtDoseC.text()
	adultCount = self.dlg.ui.txtAdultCount.text()
	aCount = str(adultCount)
	childCount = self.dlg.ui.txtChildCount.text()	
	cCount = str(childCount)

	#totalQyt = (float(totA)*float(aCount) )+ (float(totC)*float(cCount))
	totalQyt = totalQytC + totalQytA


	self.dlg.listDrugView('<tr><td width="250">'+'Budget for '+str(self.dlg.ui.lineEdit.text())+'  '+'Rs:'+' '+str(totalPrice)+'</td></tr>')
	self.dlg.listDrugView('<tr><td width="250">'+'Quantity for '+str(self.dlg.ui.lineEdit.text())+'  '+str(totalQyt)+'</td></tr>')
    



######new bud

    def viewSubdiseases(self):
	global diseaseType
	diseaseType = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbdiarrhea.currentText())
	if diseaseType == 'Diarrheal diseases':
		self.dlg.ui.cmbdiarrhea.setVisible(True)

	if diseaseType == 'Hepatis A and E':
		self.dlg.ui.cmbhepatis.setVisible(True)

	if diseaseType == 'Leptospirosis':
		self.dlg.ui.cmblept.setVisible(True)

	if diseaseType == 'ARI':
		self.dlg.ui.cmbARI.setVisible(True)

	if diseaseType == 'Measles':
		self.dlg.ui.cmbMisl.setVisible(True)

    def wellPage(self):

	self.dlg.ui.lblPlaceWell.setVisible(False)
	self.dlg.ui.lblWellId.setVisible(False)
	self.dlg.ui.lblOwnnerWell.setVisible(False)
	self.dlg.ui.lbldepthWell.setVisible(False)
	self.dlg.ui.txtDetailsa.clear()
	self.dlg.ui.chkAffectWell.setCheckState(0)
	self.dlg.ui.chkshowAllAffWell.setCheckState(0)
	self.dlg.ui.txtWellPoint.clear()

    def wsPage(self):
	self.dlg.ui.txtWellBrowser.clear()
	self.dlg.ui.chkAffectWell_3.setCheckState(0)
	self.dlg.ui.chkshowAllAffWell_3.setCheckState(0) 
	self.dlg.ui.txtWSPoint.clear()

    def popPage (self):
	self.dlg.ui.txtDetailsb.clear()
	self.dlg.ui.chkOverEighteenAff_2.setCheckState(0)
	self.dlg.ui.chkUnderEighteenAff_2.setCheckState(0)
	self.dlg.ui.chkMaleAff_2.setCheckState(0)
	self.dlg.ui.chkFeMaleAff.setCheckState(0) 
	self.dlg.ui.chkshowAllAffPopDrug.setCheckState(0)

    def clearAllManual(self):
	self.dlg.ui.txtAdultCount.clear()
	#self.dlg.ui.chkAdultCount.setCheckState(0)
	#self.dlg.ui.chkChildCount.setCheckState(0)
	self.dlg.ui.lineEdit.clear()
	self.dlg.ui.txtPrice.clear()
	self.dlg.ui.txtChildCount.clear()
	self.dlg.ui.txtDoseC.clear()
	self.dlg.ui.txtDoseA.clear()
	#self.dlg.ui.textBrowser.clear()
	self.dlg.ui.lblTotBudget.clear()
	self.dlg.ui.txtIDPPopVal.clear()
	self.dlg.ui.txtdrugMan.clear()

	drugChildQty = []
	drugAdultQty = []
	self.dlg.ui.txtTimeDay.clear()
	self.dlg.ui.txtDays.clear()
	
	

    def clearAllMisRisk(self):
	self.dlg.ui.chkAffcetedMeaslesMale.setCheckState(0)
	self.dlg.ui.chkAffcetedMeaslesFemale.setCheckState(0)
	self.dlg.ui.chkImmunizedMes.setCheckState(0)
	self.dlg.ui.txtOutBreak.clear()
	self.dlg.ui.txtOutBreak_4.clear()
	self.dlg.ui.txtOutBreak_3.clear()
	self.dlg.ui.txtOutBreak_2.clear()
	self.dlg.ui.txtOutBreak_5.clear()
	self.dlg.ui.lblMeaslImmunNormal.setVisible(False)
	self.dlg.ui.lblMeaslImmun.setVisible(False)
	self.dlg.ui.txtMeasles.clear()

    

    def clearLep(self):
	#self.dlg.ui.lblCommProven.setVisible(False)
	#self.dlg.ui.lblNotProvenLep.setVisible(False)
	#self.dlg.ui.lblMostProvenLep.setVisible(False)
	self.dlg.ui.lblLepHos.setVisible(False)
	

	

    def clearAllDrugFields(self) :
	self.dlg.ui.chkViewSubDiseases.setCheckState(0)
	self.dlg.ui.chkViewDrug.setCheckState(0)
	self.dlg.ui.chkloadDChild.setCheckState(0)
	self.dlg.ui.chkloadDAdult.setCheckState(0)

	self.dlg.ui.txtDrug1.clear()
	self.dlg.ui.txtDrug2.clear()
	self.dlg.ui.txtDrug3.clear()
	self.dlg.ui.txtDrug4.clear()

	self.dlg.ui.lblNoDys.setVisible(False)
	self.dlg.ui.lblCapSize.setVisible(False)
	self.dlg.ui.txtNoOfDays.setVisible(False)
	self.dlg.ui.txtNoOfDays.clear()
	self.dlg.ui.lblCapSize.setVisible(False)
	self.dlg.ui.lblmg1_9.setVisible(False)
	self.dlg.ui.cmbDrugSize.setVisible(False)

	self.dlg.ui.txtNoOfDays.clear()
	self.dlg.ui.txtTotQtyCount.clear()

	self.dlg.ui.lblDrugName.setVisible(False)
	self.dlg.ui.lblChildDose.setVisible(False)
	self.dlg.ui.lblAdultDose.setVisible(False)
	self.dlg.ui.lblUnitPrice.setVisible(False)
	self.dlg.ui.lblTotPrice.setVisible(False)
	self.dlg.ui.lblTotQty.setVisible(False)

	self.dlg.ui.lblmg1_9.setVisible(False)
	self.dlg.ui.lblPack1_7.setVisible(False)
	self.dlg.ui.lblmg1_10.setVisible(False)

	self.dlg.ui.txtChildDose1.clear()
	self.dlg.ui.txtChildDose2.clear()
	self.dlg.ui.txtChildDose3.clear()
	self.dlg.ui.txtChildDose4.clear()

	self.dlg.ui.txtAdultDose1.clear()
	self.dlg.ui.txtAdultDose2.clear()
	self.dlg.ui.txtAdultDose3.clear()
	self.dlg.ui.txtAdultDose4.clear()

	self.dlg.ui.txtTot1.clear()
	self.dlg.ui.txtTot2.clear()
	self.dlg.ui.txtTot3.clear()
	self.dlg.ui.txtTot4.clear()

	self.dlg.ui.txtUP1.clear()
	self.dlg.ui.txtUP2.clear()
	self.dlg.ui.txtUP3.clear()
	self.dlg.ui.txtUP4.clear()

	self.dlg.ui.txtTotQty1.clear()
	self.dlg.ui.txtTotQty2.clear()
	self.dlg.ui.txtTotQty3.clear()
	self.dlg.ui.txtTotQty4.clear()

	self.dlg.ui.txtDrug1.setVisible(False)
	self.dlg.ui.txtChildDose1.setVisible(False)
	self.dlg.ui.txtAdultDose1.setVisible(False)
	self.dlg.ui.txtUP1.setVisible(False)
	self.dlg.ui.btnAddD1.setVisible(False)
	#self.dlg.ui.txtTot1.setVisible(False)
	self.dlg.ui.txtTotQty1.setVisible(False)

	self.dlg.ui.txtDrug2.setVisible(False)
	self.dlg.ui.txtChildDose2.setVisible(False)
	self.dlg.ui.txtAdultDose2.setVisible(False)
	self.dlg.ui.txtUP2.setVisible(False)
	self.dlg.ui.btnAddD2.setVisible(False)
	self.dlg.ui.txtTot2.setVisible(False)
	self.dlg.ui.txtTotQty2.setVisible(False)

	self.dlg.ui.txtDrug3.setVisible(False)
	self.dlg.ui.txtChildDose3.setVisible(False)
	self.dlg.ui.txtAdultDose3.setVisible(False)
	self.dlg.ui.txtUP3.setVisible(False)
	self.dlg.ui.btnAddD3.setVisible(False)
	self.dlg.ui.txtTot3.setVisible(False)
	self.dlg.ui.txtTotQty3.setVisible(False)

	self.dlg.ui.txtDrug4.setVisible(False)
	self.dlg.ui.txtChildDose4.setVisible(False)
	self.dlg.ui.txtAdultDose4.setVisible(False)
	self.dlg.ui.txtUP4.setVisible(False)
	self.dlg.ui.btnAddD4.setVisible(False)
	self.dlg.ui.txtTot4.setVisible(False)
	self.dlg.ui.txtTotQty4.setVisible(False) #


	self.dlg.ui.lblmg1.setVisible(False)
	self.dlg.ui.lblmg1_2.setVisible(False)
	self.dlg.ui.lblmg1_3.setVisible(False)
	self.dlg.ui.lblmg1_4.setVisible(False)
	self.dlg.ui.lblmg1_5.setVisible(False)
	self.dlg.ui.lblmg1_6.setVisible(False)
	self.dlg.ui.lblPack1.setVisible(False)
	self.dlg.ui.lblPack1_2.setVisible(False)
	self.dlg.ui.lblPack1_3.setVisible(False)
	self.dlg.ui.lblPack1_4.setVisible(False)
	self.dlg.ui.lblPack1_5.setVisible(False)
	self.dlg.ui.lblPack1_6.setVisible(False) 

	self.dlg.ui.txtTime.setVisible(False)
	self.dlg.ui.txtTime_2.setVisible(False) 
	self.dlg.ui.lblmg1_7.setVisible(False)
	self.dlg.ui.lblmg1_8.setVisible(False) 
	self.dlg.ui.txtAllTota.setVisible(False)
	


	self.dlg.ui.txtDrug2.setText(str())
	self.dlg.ui.txtChildDose2.setText(str(0))
	self.dlg.ui.txtAdultDose2.setText(str(0))
	self.dlg.ui.txtUP2.setText(str(0))
	#self.dlg.ui.btnAddD2.setText(str(textToShow))
	self.dlg.ui.txtTot2.setText(str(0.0))
	self.dlg.ui.txtTotQty2.setText(str(0.0))
	#self.dlg.ui.grpDrugs.setVisible(False)

	self.dlg.ui.txtDrug3.setText(str())
	self.dlg.ui.txtChildDose3.setText(str(0))
	self.dlg.ui.txtAdultDose3.setText(str(0))
	self.dlg.ui.txtUP3.setText(str(0))
	#self.dlg.ui.btnAddD2.setText(str(textToShow))
	self.dlg.ui.txtTot3.setText(str(0.0))
	self.dlg.ui.txtTotQty3.setText(str(0.0))
	#self.dlg.ui.grpDrugs.setVisible(False)

	self.dlg.ui.txtDrug4.setText(str())
	self.dlg.ui.txtChildDose4.setText(str(0))
	self.dlg.ui.txtAdultDose4.setText(str(0))
	self.dlg.ui.txtUP4.setText(str(0))
	#self.dlg.ui.btnAddD2.setText(str(textToShow))
	self.dlg.ui.txtTot4.setText(str(0.0))
	self.dlg.ui.txtTotQty4.setText(str(0.0))
	#self.dlg.ui.grpDrugs.setVisible(False)

	self.dlg.ui.cmbdiarrhea.setVisible(False)
	self.dlg.ui.cmbhepatis.setVisible(False)
	self.dlg.ui.cmblept.setVisible(False)
	self.dlg.ui.cmbARI.setVisible(False)
	self.dlg.ui.cmbMisl.setVisible(False)

	self.dlg.ui.txtDrug1.setVisible(False)
	self.dlg.ui.txtChildDose1.setVisible(False)
	self.dlg.ui.txtAdultDose1.setVisible(False)
	self.dlg.ui.txtUP1.setVisible(False)
	self.dlg.ui.btnAddD1.setVisible(False)
	#self.dlg.ui.txtTot1.setVisible(False)
	self.dlg.ui.txtTotQty1.setVisible(False)

	self.dlg.ui.txtDrug2.setVisible(False)
	self.dlg.ui.txtChildDose2.setVisible(False)
	self.dlg.ui.txtAdultDose2.setVisible(False)
	self.dlg.ui.txtUP2.setVisible(False)
	self.dlg.ui.btnAddD2.setVisible(False)
	self.dlg.ui.txtTot2.setVisible(False)
	self.dlg.ui.txtTotQty2.setVisible(False)

	self.dlg.ui.txtDrug3.setVisible(False)
	self.dlg.ui.txtChildDose3.setVisible(False)
	self.dlg.ui.txtAdultDose3.setVisible(False)
	self.dlg.ui.txtUP3.setVisible(False)
	self.dlg.ui.btnAddD3.setVisible(False)
	self.dlg.ui.txtTot3.setVisible(False)
	self.dlg.ui.txtTotQty3.setVisible(False)

	self.dlg.ui.txtDrug4.setVisible(False)
	self.dlg.ui.txtChildDose4.setVisible(False)
	self.dlg.ui.txtAdultDose4.setVisible(False)
	self.dlg.ui.txtUP4.setVisible(False)
	self.dlg.ui.btnAddD4.setVisible(False)
	self.dlg.ui.txtTot4.setVisible(False)
	self.dlg.ui.txtTotQty4.setVisible(False) #


	self.dlg.ui.lblmg1.setVisible(False)
	self.dlg.ui.lblmg1_2.setVisible(False)
	self.dlg.ui.lblmg1_3.setVisible(False)
	self.dlg.ui.lblmg1_4.setVisible(False)
	self.dlg.ui.lblmg1_5.setVisible(False)
	self.dlg.ui.lblmg1_6.setVisible(False)
	self.dlg.ui.lblPack1.setVisible(False)
	self.dlg.ui.lblPack1_2.setVisible(False)
	self.dlg.ui.lblPack1_3.setVisible(False)
	self.dlg.ui.lblPack1_4.setVisible(False)
	self.dlg.ui.lblPack1_5.setVisible(False)
	self.dlg.ui.lblPack1_6.setVisible(False) 

	self.dlg.ui.txtTime.setVisible(False)
	self.dlg.ui.txtTime_2.setVisible(False)

	drugNameList = []
	drugPriceList = []
	doseChildrenList = []
	doseAdultList = []
	drugPrice = []

	self.dlg.ui.txtAdQ1.clear()
	self.dlg.ui.txtChQ1.clear()
	
	


    def viewDrugDetailsFever(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbdiarrhea.currentText())
	if disease == 'Fever' and mainDisease == 'Diarrheal diseases':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		#self.dlg.ui.lblTotPrice.setVisible(True)
		#self.dlg.ui.lblTotQty.setVisible(True)
		
		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		#self.dlg.ui.txtTot1.setVisible(True)
		#self.dlg.ui.txtTotQty1.setVisible(True)

		self.dlg.ui.txtDrug1.setText('paracetamol')
		self.dlg.ui.txtChildDose1.setText('15')
		self.dlg.ui.txtAdultDose1.setText('1000') 

		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)




    def viewDrugDetailsDiarrhea(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbdiarrhea.currentText())
	if disease == 'Diarrhea' and mainDisease == 'Diarrheal diseases':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		#self.dlg.ui.lblTotPrice.setVisible(True)
		#self.dlg.ui.lblTotQty.setVisible(True)

		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)


		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		#self.dlg.ui.lblPack1_7.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		#self.dlg.ui.txtTot1.setVisible(True)
		#self.dlg.ui.txtTotQty1.setVisible(True)

		self.dlg.ui.txtDrug1.setText('Rehydration Solution')
		self.dlg.ui.txtChildDose1.setText('1')
		self.dlg.ui.txtAdultDose1.setText('2') 
		self.dlg.ui.lblPack1.setVisible(True)
		self.dlg.ui.lblPack1_2.setVisible(True)
		#self.dlg.ui.lblPack1_7.setVisible(True)
		

    def viewDrugDetailsVomotting(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbdiarrhea.currentText())
	if disease == 'Vomotting' and mainDisease == 'Diarrheal diseases':

		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		#self.dlg.ui.lblTotPrice.setVisible(True)
		#self.dlg.ui.lblTotQty.setVisible(True)

		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)


		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		self.dlg.ui.txtTot1.setVisible(True)
		#self.dlg.ui.txtTotQty1.setVisible(True)

		self.dlg.ui.txtDrug1.setText('Domperidone')
		self.dlg.ui.txtChildDose1.setText('5')
		self.dlg.ui.txtAdultDose1.setText('10') #
		self.dlg.ui.lblmg1.setVisible(True)


    def viewDrugDetailsBacterialDiarrhea(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbdiarrhea.currentText())
	if disease == 'Antibiotics - Ciprofloxacins' and mainDisease == 'Diarrheal diseases':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		#self.dlg.ui.lblTotPrice.setVisible(True)
		#.dlg.ui.lblTotQty.setVisible(True)

		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)

		#self.dlg.ui.txtUP2.clear() 
		#self.dlg.ui.txtTot2.clear()
		#self.dlg.ui.txtTotQty2.clear()
		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		

		self.dlg.ui.txtDrug2.setText('Ciprofloxacin')
		self.dlg.ui.txtChildDose2.setText('0')
		self.dlg.ui.txtAdultDose2.setText('500')

    def viewDrugDetailsCephalexin(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbdiarrhea.currentText())
	if disease == 'Bacterial Infection' and mainDisease == 'Diarrheal diseases':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		#self.dlg.ui.lblTotPrice.setVisible(True)
		#self.dlg.ui.lblTotQty.setVisible(True)

		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)

		
		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)

	
		
		self.dlg.ui.txtDrug1.setText('Cephalexin')
		self.dlg.ui.txtChildDose1.setText('250')
		self.dlg.ui.txtAdultDose1.setText('500')

		


    def viewDrugDetailsCiprofloxacin(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbdiarrhea.currentText())
	if disease == 'Antibiotics - Ciprofloxacin' and mainDisease == 'Diarrheal diseases':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		

		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)

		
		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		

		self.dlg.ui.txtDrug1.setText('Cephalexin')
		self.dlg.ui.txtChildDose1.setText('250')
		self.dlg.ui.txtAdultDose1.setText('500')

		

    def viewDrugDetailsMusclePain(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbMisl.currentText())
	if disease == 'Muscle Pain' and mainDisease == 'Measles':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		
		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)

		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		

		self.dlg.ui.txtDrug1.setText('paracetamol')
		self.dlg.ui.txtChildDose1.setText('15')
		self.dlg.ui.txtAdultDose1.setText('1000') 

    def viewDrugDetailsMisFever(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbMisl.currentText())
	if disease == 'Fever' and mainDisease == 'Measles':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		
		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)

		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		

		self.dlg.ui.txtDrug1.setText('paracetamol')
		self.dlg.ui.txtChildDose1.setText('15')
		self.dlg.ui.txtAdultDose1.setText('1000') #cmblept


    def viewDrugDetailsFeverHepatis(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbhepatis.currentText())
	if disease == 'Fever' and mainDisease == 'Hepatis A and E':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		

		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)

		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		
		self.dlg.ui.txtDrug1.setText('paracetamol')
		self.dlg.ui.txtChildDose1.setText('15')
		self.dlg.ui.txtAdultDose1.setText('1000') 

  

    def viewDrugDetailsDiarrheaHepatis(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbhepatis.currentText())
	if disease == 'Diarrhea' and mainDisease == 'Hepatis A and E':

		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		
	
		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)


		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		
		self.dlg.ui.txtDrug1.setText('Oral Rehydration Solution')
		self.dlg.ui.txtChildDose1.setText('1')
		self.dlg.ui.txtAdultDose1.setText('2') 

    def viewDrugDetailsVomottingHepatis(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbhepatis.currentText())
	if disease == 'Vomotting' and mainDisease == 'Hepatis A and E':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		
		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)

		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		
		self.dlg.ui.txtDrug1.setText('Domperidone')
		self.dlg.ui.txtChildDose1.setText('5')
		self.dlg.ui.txtAdultDose1.setText('10') #


    def viewDrugDetailsMusclePainLepatos(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmblept.currentText())
	if disease == 'Muscle Pain' and mainDisease == 'Leptospirosis':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		
		self.dlg.ui.lblmg1.setVisible(True)
		self.dlg.ui.lblmg1_2.setVisible(True)
		
		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)


		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		
		self.dlg.ui.txtDrug1.setText('paracetamol')
		self.dlg.ui.txtChildDose1.setText('15')
		self.dlg.ui.txtAdultDose1.setText('1000') 


    def viewDrugDetailsFeverLepatos(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmblept.currentText())
	if disease == 'Fever' and mainDisease == 'Leptospirosis':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		
		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)



		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		

		self.dlg.ui.lblmg1.setVisible(True)
		self.dlg.ui.lblmg1_2.setVisible(True)

		self.dlg.ui.txtDrug1.setText('Paracetamol')
		self.dlg.ui.txtChildDose1.setText('15')
		self.dlg.ui.txtAdultDose1.setText('1000')

		

    def viewDrugDetailsPenicilineLepatos(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmblept.currentText())
	if disease == 'Bacterial Infection' and mainDisease == 'Leptospirosis':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		

		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)


		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		
		self.dlg.ui.txtDrug1.setText('Peniciline')
		self.dlg.ui.txtChildDose1.setText('25')
		self.dlg.ui.txtAdultDose1.setText('600')
		self.dlg.ui.lblmg1.setVisible(True)
		self.dlg.ui.lblmg1_2.setVisible(True)

    def viewDrugDetailsFeverARI(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbARI.currentText())
	if disease == 'Fever' and mainDisease == 'ARI':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		
		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)

		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		
		self.dlg.ui.txtDrug1.setText('paracetamol')
		self.dlg.ui.txtChildDose1.setText('15')
		self.dlg.ui.txtAdultDose1.setText('1000') 

		self.dlg.ui.lblmg1.setVisible(True)
		self.dlg.ui.lblmg1_2.setVisible(True)

    def viewDrugDetailsVomottingARI(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbARI.currentText())
	if disease == 'Vomotting' and mainDisease == 'ARI':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		
		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)

		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		

		self.dlg.ui.txtDrug1.setText('Domperidone')
		self.dlg.ui.txtChildDose1.setText('5')
		self.dlg.ui.txtAdultDose1.setText('10')

		self.dlg.ui.lblmg1.setVisible(True)
		self.dlg.ui.lblmg1_2.setVisible(True)

    def viewDrugDetailsCoughARI(self):
	mainDisease = str(self.dlg.ui.comboBox_2.currentText())
	global disease 
	disease = str(self.dlg.ui.cmbARI.currentText())
	if disease == 'Cough' and mainDisease == 'ARI':
		self.dlg.ui.lblDrugName.setVisible(True)
		self.dlg.ui.lblChildDose.setVisible(True)
		self.dlg.ui.lblAdultDose.setVisible(True)
		self.dlg.ui.lblUnitPrice.setVisible(True)
		
		self.dlg.ui.lblNoDys.setVisible(True)
		self.dlg.ui.txtNoOfDays.setVisible(True)
		self.dlg.ui.lblCapSize.setVisible(True)
		self.dlg.ui.cmbDrugSize.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)

		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.lblmg1_9.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		
		self.dlg.ui.txtDrug1.setText('Salbutamol')
		self.dlg.ui.txtChildDose1.setText('250')
		self.dlg.ui.txtAdultDose1.setText('500')

		self.dlg.ui.lblmg1.setVisible(True)
		self.dlg.ui.lblmg1_2.setVisible(True)


    def selectConditionARI(self): 
		mainDisease = str(self.dlg.ui.comboBox_2.currentText())
		condition = str(self.dlg.ui.cmbARI.currentText())
		if condition == 'Fever' and mainDisease == 'ARI': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('6')


		if condition == 'Vomotting' and mainDisease == 'ARI': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('8')

		if condition == 'Cough' and mainDisease == 'ARI': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('8')

    

    def selectCondition(self): 
		mainDisease = str(self.dlg.ui.comboBox_2.currentText())
		condition = str(self.dlg.ui.cmbdiarrhea.currentText())
		if condition == 'Fever' and mainDisease == 'Diarrheal diseases': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			 
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('6')
		

		if condition == 'Diarrhea' and mainDisease == 'Diarrheal diseases': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			
			self.dlg.ui.lblPack1.setVisible(True)
			self.dlg.ui.lblPack1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('1')

		if condition == 'Vomotting' and mainDisease == 'Diarrheal diseases': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			#self.dlg.ui.lblPack1_7.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			#self.dlg.ui.txtTot1.setVisible(True)
			#self.dlg.ui.txtTotQty1.setVisible(True) 
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('8')

		if condition == 'Bacterial Infection' and mainDisease == 'Diarrheal diseases': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			#self.dlg.ui.lblPack1_7.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			#self.dlg.ui.txtTot1.setVisible(True)
			#self.dlg.ui.txtTotQty1.setVisible(True) 
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('8')
			

		

    def selectConditionMisc(self): #cmbMisl
		mainDisease = str(self.dlg.ui.comboBox_2.currentText()) #Measles
		condition = str(self.dlg.ui.cmbMisl.currentText())

		if condition == 'Fever' and mainDisease == 'Measles': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			#self.dlg.ui.txtTot1.setVisible(True)
			#self.dlg.ui.txtTotQty1.setVisible(True) 
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('6')

		if condition == 'Muscle Pain' and mainDisease == 'Measles':
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			#self.dlg.ui.txtTot1.setVisible(True)
			#self.dlg.ui.txtTotQty1.setVisible(True) 
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('6')
    def selectConditionHepatis(self):  # Hepatis A and E
		mainDisease = str(self.dlg.ui.comboBox_2.currentText())
		condition = str(self.dlg.ui.cmbhepatis.currentText())
		if condition == 'Fever' and mainDisease == 'Hepatis A and E': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			#self.dlg.ui.txtTot1.setVisible(True)
			#self.dlg.ui.txtTotQty1.setVisible(True) 
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('6')
		

		if condition == 'Diarrhea' and mainDisease == 'Hepatis A and E': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			#self.dlg.ui.txtTot1.setVisible(True)
			#self.dlg.ui.txtTotQty1.setVisible(True) 
			self.dlg.ui.lblPack1.setVisible(True)
			self.dlg.ui.lblPack1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('1')

		if condition == 'Vomotting' and mainDisease == 'Hepatis A and E': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			#self.dlg.ui.txtTot1.setVisible(True)
			#self.dlg.ui.txtTotQty1.setVisible(True) 
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.txtTime.setText('8')

		


    def selectConditionLepatos(self): 
		mainDisease = str(self.dlg.ui.comboBox_2.currentText()) #Leptospirosis
		condition = str(self.dlg.ui.cmblept.currentText())

		if condition == 'Fever' and mainDisease == 'Leptospirosis': 
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtDrug2.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtChildDose2.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtAdultDose2.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.txtUP2.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.lblmg1_10.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			self.dlg.ui.btnAddD2.setVisible(True)
			#self.dlg.ui.txtTot1.setVisible(True)
			self.dlg.ui.txtTot2.setVisible(True)
			#self.dlg.ui.txtTotQty1.setVisible(True) 
			self.dlg.ui.txtTotQty2.setVisible(True) 
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.lblmg1_3.setVisible(True)
			self.dlg.ui.lblmg1_4.setVisible(True) #lblmg1_10
			self.dlg.ui.lblmg1_10.setVisible(True)
			self.dlg.ui.txtTime.setText('6')

		if condition == 'Muscle Pain' and mainDisease == 'Leptospirosis':
			self.dlg.ui.txtDrug1.setVisible(True)
			self.dlg.ui.txtDrug2.setVisible(True)
			self.dlg.ui.txtChildDose1.setVisible(True)
			self.dlg.ui.txtChildDose2.setVisible(True)
			self.dlg.ui.txtAdultDose1.setVisible(True)
			self.dlg.ui.txtAdultDose2.setVisible(True)
			self.dlg.ui.txtUP1.setVisible(True)
			self.dlg.ui.txtUP2.setVisible(True)
			self.dlg.ui.lblmg1_9.setVisible(True)
			self.dlg.ui.lblmg1_10.setVisible(True)
			self.dlg.ui.btnAddD1.setVisible(True)
			self.dlg.ui.btnAddD2.setVisible(True)
			#self.dlg.ui.txtTot1.setVisible(True)
			self.dlg.ui.txtTot2.setVisible(True)
			#self.dlg.ui.txtTotQty1.setVisible(True) 
			self.dlg.ui.txtTotQty2.setVisible(True) 
			self.dlg.ui.lblmg1.setVisible(True)
			self.dlg.ui.lblmg1_2.setVisible(True)
			self.dlg.ui.lblmg1_3.setVisible(True)
			self.dlg.ui.lblmg1_4.setVisible(True) 
			self.dlg.ui.txtTime.setText('6')

		


		self.dlg.ui.txtDrug3.setVisible(True)
		self.dlg.ui.txtDrug3.setText('penicilline')
		self.dlg.ui.txtChildDose3.setVisible(True)
		self.dlg.ui.txtChildDose3.setText('25')
		self.dlg.ui.txtAdultDose3.setVisible(True)
		self.dlg.ui.txtChildDose3.setText('1.2')
		self.dlg.ui.txtUP3.setVisible(True)
		self.dlg.ui.btnAddD3.setVisible(True)
		self.dlg.ui.txtTot3.setVisible(True)
		self.dlg.ui.txtTotQty3.setVisible(True) 
		self.dlg.ui.lblmg1_5.setVisible(True)
		self.dlg.ui.lblmg1_6.setVisible(True)
		self.dlg.ui.txtTime.setText('6')

		self.dlg.ui.txtDrug3.setVisible(True)
		self.dlg.ui.txtDrug3.setText('Doxycycline')
		self.dlg.ui.txtChildDose3.setVisible(True)
		self.dlg.ui.txtChildDose3.setText('0')
		self.dlg.ui.txtAdultDose3.setVisible(True)
		self.dlg.ui.txtChildDose3.setText('200')
		self.dlg.ui.txtUP3.setVisible(True)
		self.dlg.ui.btnAddD3.setVisible(True)
		self.dlg.ui.txtTot3.setVisible(True)
		self.dlg.ui.txtTotQty3.setVisible(True) 
		self.dlg.ui.lblmg1_5.setVisible(True)
		self.dlg.ui.lblmg1_6.setVisible(True)
		self.dlg.ui.txtTime.setText('6')

		self.dlg.ui.txtDrug1.setVisible(True)
		self.dlg.ui.txtChildDose1.setVisible(True)
		self.dlg.ui.txtAdultDose1.setVisible(True)
		self.dlg.ui.txtUP1.setVisible(True)
		self.dlg.ui.btnAddD1.setVisible(True)
		#self.dlg.ui.txtTot1.setVisible(True)
		#self.dlg.ui.txtTotQty1.setVisible(True) 
		self.dlg.ui.lblmg1.setVisible(True)
		self.dlg.ui.lblmg1_2.setVisible(True)
		self.dlg.ui.txtTime_2.setText('1')


    def calcTotBug(self): #str(drugPrice[x]


		style = getSampleStyleSheet()	
		pdf = SimpleDocTemplate("Medicinal Drugs Estimation - With Pre-defined Details two - FLOOgin Report.pdf")
		clBl = '<font color="blue">'
		clBls = '</font>'
		clR = '<font color="red">'
		clRs = '</font>'
		h2 = '<h1>'
		h2s = '</h1>'
		detailsBudget2.append( h2 + clR + "<b>Medicinal Drugs Estimation - With Pre-defined Details two- FLOOgin Report </b>" + clRs + h2s )
		global floodLyrForBudRpt2

		crs = str(self.iface.activeLayer().crs().authid())
		now = datetime.datetime.now()
		date = now.strftime("%Y-%m-%d")
		time = now.strftime("%H:%M")

		detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " #+ clBl + str(floodLyrForBudRpt) + clBls
		detDateTime = "Generated on : " + date + " at " + time
		detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
		detailsBudget2.append(str(detHazard))
		detailsBudget2.append(str(detDateTime))
		detailsBudget2.append(str(detCrs))
		#global drugPrice
		#drugPrice = []
		global totalPrice 
		totalPrice = 0
		global totAdult 
		totAdult = 0
		global totChild 
		totChild = 0

		self.dlg.ui.lblRs.setVisible(True)

		global storyBudget2
		storyBudget2 = []
		global drugReport2
		drugReport2 =[]
		global detailsBudget2
		detailsBudget2 = []

		tb='<table style="width:500px"><tr><th width="180" align="left">Total Price</th><th width="180" align="left">Total Adult Quantity</th><th width="180" align="left">Total Child Quantity</th><</tr>'


		styles = getSampleStyleSheet()
		nmm = Paragraph('''<b>Total Price</b>''',styles["Normal"])
		tpp = Paragraph('''<b>Total Adult Quantity</b>''',styles["Normal"])
		css = Paragraph('''<b>Total Child Quantity</b>''',styles["Normal"])
		
		detailsBudget2.append( [ nmm, tpp, css] )
		
		for x in range(0, len(drugPriceListb)):
			price =  drugPriceListb[x]
			totalPrice = float(totalPrice) + float(price) 
		detailsBudget2.append(str(totalPrice))
		
		for x in range(0, len(childtotList)):
			chiltQ =  childtotList[x]
			totChild = float(chiltQ) + float(totChild) 
		detailsBudget2.append(str(totChild))
		
		for x in range(0, len(adultotList)):
			adultQ =  adultotList[x]
			totAdult = float(adultQ) + float(totAdult)
		detailsBudget2.append(str(totAdult))

		#totalPrice = totalPriceG - totmin
		totaQty = totChild + totAdult	
		#self.dlg.listDrugDetails('<tr><td width="250">'+'Total Budget value = '+'Rs: '+str(totalPrice)+'</td></tr>')	
		#self.dlg.listDrugDetails('<tr><td width="250">'+'Total Budget value = '+'Rs: '+str(totaQty)+'</td></tr>')

		#drugReport2.append( str(totalPrice), str(totChild) , str(totAdult) )
		
		self.dlg.ui.lblDrugTotaLast.setText('Rs' + ' ' +str(totalPrice))

		tbWell = Table(detailsBudget2)#
		storyWelRep.append( tbWell ) #
		pdf.build(storyWelRep)#


    def viewDetailsDrug1(self): # start

		style = getSampleStyleSheet()	
		pdf = SimpleDocTemplate("Medicinal Drugs Estimation - With Pre-defined Details - FLOOgin Report.pdf")
		clBl = '<font color="blue">'
		clBls = '</font>'
		clR = '<font color="red">'
		clRs = '</font>'
		h2 = '<h1>'
		h2s = '</h1>'
		detailsBudget2.append( h2 + clR + "<b>Medicinal Drugs Estimation - With Pre-defined Details - FLOOgin Report </b>" + clRs + h2s )
		global floodLyrForBudRpt2

		crs = str(self.iface.activeLayer().crs().authid())
		now = datetime.datetime.now()
		date = now.strftime("%Y-%m-%d")
		time = now.strftime("%H:%M")

		detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " #+ clBl + str(floodLyrForBudRpt) + clBls
		detDateTime = "Generated on : " + date + " at " + time
		detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
		detailsBudget2.append(str(detHazard))
		detailsBudget2.append(str(detDateTime))
		detailsBudget2.append(str(detCrs))


		priceForOne = 0
		
		global percentChild 
		percentChild = (float(self.dlg.ui.cmbDChild.currentText())) / 100.0
		global percentAdult
		percentAdult = (float(self.dlg.ui.cmbDAdult.currentText())) / 100.0

		

		drugName = self.dlg.ui.txtDrug1.text() #df1
		DName = str(drugName)
		
		dUnitPrice = self.dlg.ui.txtUP1.text() #rd1
		DUnit = str(dUnitPrice)
		
		dChildDose = self.dlg.ui.txtChildDose1.text() #cf1
		DChild = str(dChildDose)
		
		adultDose = self.dlg.ui.txtAdultDose1.text()#af1
		DAdult = str(adultDose)
		
		ageChild = 0
		ageAdult = 0
		ageChildPercent = 0
		ageAdultPercent = 0
		popFloodLayer = self.iface.activeLayer()

		
		if self.dlg.ui.chkloadDChild.isChecked():
		    for feature in popFloodLayer.getFeatures():
			 child = feature['AGE_U_18']
			 ageChild = ageChild + child
			 ageChildPercent = ageChild * percentChild
		
		if self.dlg.ui.chkloadDAdult.isChecked():
		    for feature in popFloodLayer.getFeatures():
			 adult = feature['AGE_O_18']
			 ageAdult = ageAdult + adult
			 ageAdultPercent = ageAdult * percentAdult


		global storyBudget2
		storyBudget2 = []
		global drugReport2
		drugReport2 =[]
		global detailsBudget2
		detailsBudget2 = []
		

		timePerDay = 0
   		drugNameList.append(DName)
   		drugPriceList.append(DUnit)#rd1
   		doseChildrenList.append(DChild)
   		doseAdultList.append(DAdult)
		timeCount = self.dlg.ui.txtTime.text()
		timePerDay = 24.0 / float(timeCount)
		CountNumberOfDays = self.dlg.ui.txtNoOfDays.text()
		numberOfDays = float(CountNumberOfDays)

		qtyAsCapSize = float(str(self.dlg.ui.cmbDrugSize.currentText()))
		givCmb2.append(str(qtyAsCapSize))

		priceForOneTime = (ageAdultPercent * float(DUnit) * float(DAdult)) + (ageChildPercent * float(DUnit) * float(DChild))

		priceForOne = priceForOneTime * timePerDay * numberOfDays

		adultDoseTot = (ageAdultPercent * timePerDay * numberOfDays * float(DAdult)) / qtyAsCapSize

		childDoseTot = (ageChildPercent * timePerDay * numberOfDays * float(DChild)) / qtyAsCapSize

		#drugPrice.append(str(priceForOne)) 
		drugPriceListb.append(str(priceForOne))
		totalPrice = str(self.dlg.ui.txtTot1.text())

		totalAdCount = str(self.dlg.ui.txtTot3.text())
		totalChCount = str(self.dlg.ui.txtTot4.text())

		adultotList.append(str(adultDoseTot))
		childtotList.append(str(childDoseTot))

		self.dlg.ui.textBrowser_2.clear()
	
		tb='<table style="width:500px"><tr><th width="120" align="left">Name</th><th width="75" align="left">Size(mg/ml)</th><th width="75" align="left">Unit_Price</th><th width="75" align="left">Child_Qty</th><th width="75" align="left">Adult_Qty</th><th width="75" align="left">Price</th><</tr>'


		styles = getSampleStyleSheet()
		nm = Paragraph('''<b>NAME</b>''',styles["Normal"])
		tp = Paragraph('''<b>Unit Price</b>''',styles["Normal"])
		cs = Paragraph('''<b>Child Qty</b>''',styles["Normal"])
		md = Paragraph('''<b>Adult Qty</b>''',styles["Normal"])
		pd = Paragraph('''<b>Price</b>''',styles["Normal"])
		css = Paragraph('''<b>Capsual Size (mg or ml)</b>''',styles["Normal"])
		drugReport2.append( [ nm, tp, cs, md , pd , css] )		

		self.dlg.listDrugDetails(tb)


		for x in range(0, len(drugNameList)): 
		

			
	                self.dlg.ui.txtTot1.setText(str(drugPriceListb[x]))
			viewtot = str(self.dlg.ui.txtTot1.text())
			self.dlg.ui.txtAdQ1.setText(str(adultotList[x]))
			self.dlg.ui.txtChQ1.setText(str(childtotList[x]))
			#self.dlg.ui.txtTotQty4.setText(str(drugPrice[x]))
			adultDose = float(str(self.dlg.ui.txtAdQ1.text())) * adultDoseTot
			childDose = float(str(self.dlg.ui.txtChQ1.text())) * childDoseTot
			

			self.dlg.listDrugDetails('<tr><td width="120">'+str(drugNameList[x])+'</td><td width="75">'+str(givCmb2[x])+'</td><td width="75">'+str(drugPriceList[x])+'</td><td width="75">'+str(childtotList[x])+'</td><td width="75">'+str(adultotList[x])+'</td><td width="75">'+str(viewtot)+'</td></tr>')


			aduktQty = self.dlg.ui.txtAdQ1.text()
			childQty = self.dlg.ui.txtChQ1.text()
			totQty = (float(aduktQty) * float(ageAdultPercent) ) + (float(childQty) * float(ageChildPercent) )
			self.dlg.ui.txtTotQty1.setText(str(totQty)) #txtTotQtyCount
			qtyCal = self.dlg.ui.txtTotQty1.text()
			qtyCal1 = str(qtyCal)

			drugReport2.append( [str(str(drugNameList[x])), str(qtyAsCapSize),str(drugPriceList[x]) , str(childtotList[x]) , str(adultotList[x]) , str(viewtot) ] )

			tbWell = Table(drugReport2)#
			storyWelRep.append( tbWell ) #
			pdf.build(storyWelRep)#
			
			global drugQtySize
			drugQtySize = str(self.dlg.ui.cmbDrugSize.currentText())
			if drugQtySize == '500':
				#qtyCalc = float(qtyCal1) / 500.0
				qtyCalc = float(viewtot) / 500.0
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

			if drugQtySize == '250':
				#qtyCalc = float(qtyCal1) / 250.0
				qtyCalc = float(viewtot) / 250.00
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

			if drugQtySize == '100':
				#qtyCalc = float(qtyCal1) / 100.0
				qtyCalc = float(viewtot) / 100.00
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

			if drugQtySize == '25':
				#qtyCalc = float(qtyCal1) / 100.0
				qtyCalc = float(viewtot) / 25.00
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

			if drugQtySize == '50':
				#qtyCalc = float(qtyCal1) / 100.0
				qtyCalc = float(viewtot) / 50.00
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

			if drugQtySize == '750':
				#qtyCalc = float(qtyCal1) / 100.0
				qtyCalc = float(viewtot) / 750.00
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

			if drugQtySize == '1000':
				#qtyCalc = float(qtyCal1) / 100.0
				qtyCalc = float(viewtot) / 1000.00
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))
			
			viewqty = float(str(self.dlg.ui.txtTotQtyCount.text()))

			


    def calcQty1(self):
		priceForOne = 0
		
		global percentChild 
		percentChild = float(self.dlg.ui.cmbDChild.currentText())
		global percentAdult
		percentAdult = float(self.dlg.ui.cmbDAdult.currentText())

	
		
		df2 = self.dlg.ui.txtDrug2.text()
		d2 = str(df2)
		
		rd2 = self.dlg.ui.txtUP2.text()
		r2 = str(rd2)
		
		cf2 = self.dlg.ui.txtChildDose2.text()
		c2 = str(cf2)
		
		af2 = self.dlg.ui.txtAdultDose2.text()
		a2 = str(af2)
		
		ageChild = 0
		ageAdult = 0
		ageChildPercent = 0
		ageAdultPercent = 0
		popFloodLayer = self.iface.activeLayer()
		
		if self.dlg.ui.chkloadDChild.isChecked():
		    for feature in popFloodLayer.getFeatures():
			 child = feature['AGE_U_18']
			 ageChild = ageChild + child
			 ageChildPercent = ageChild * percentChild

		
		if self.dlg.ui.chkloadDAdult.isChecked():
		    for feature in popFloodLayer.getFeatures():
			 adult = feature['AGE_O_18']
			 ageAdult = ageAdult + adult
			 ageAdultPercent = ageAdult * percentAdult

		
	
		timePerDay = 0	
   		drugNameList.append(d2)
   		drugPriceList.append(r2)
   		doseChildrenList.append(c2)
   		doseAdultList.append(a2)
		CountNumberOfDays = self.dlg.ui.txtNoOfDays.text()
		numberOfDays = float(CountNumberOfDays)
		timeCount = self.dlg.ui.txtTime.text()
		timePerDay = 24.0 / float(timeCount)
		priceForOneTime = (ageAdultPercent * float(r2) * float(c2)) + (ageChildPercent * float(r2) * float(a2))#((100 * float(s)) #* float(c) ) + (150 * float(s) * float(a) )
		priceForOne = priceForOneTime * timePerDay * numberOfDays
		drugPrice.append(str(priceForOne))
	
		
	
		for x in range(0, len(drugNameList)):
		
	   		
			self.dlg.ui.txtAdQ2.setText(str(doseAdultList[x]))
			self.dlg.ui.txtChQ2.setText(str(doseChildrenList[x]))
			aduktQty = self.dlg.ui.txtAdQ2.text()
			childQty = self.dlg.ui.txtChQ2.text()
			totQty = (float(aduktQty) * float(ageAdultPercent) ) + (float(childQty) * float(ageChildPercent) )
			self.dlg.ui.txtTotQty2.setText(str(totQty))

    def calcQty2(self):
		priceForOne = 0
		
		global percentChild 
		percentChild = float(self.dlg.ui.cmbDChild.currentText())
		global percentAdult
		percentAdult = float(self.dlg.ui.cmbDAdult.currentText())
	
		
		df2 = self.dlg.ui.txtDrug3.text()
		d2 = str(df2)
		
		rd2 = self.dlg.ui.txtUP3.text()
		r2 = str(rd2)
		
		cf2 = self.dlg.ui.txtChildDose3.text()
		c2 = str(cf2)
		
		af2 = self.dlg.ui.txtAdultDose3.text()
		a2 = str(af2)
		
		ageChild = 0
		ageAdult = 0
		ageChildPercent = 0
		ageAdultPercent = 0
		popFloodLayer = self.iface.activeLayer()
		if self.dlg.ui.chkloadDChild.isChecked():
		   for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChild = ageChild + child
			ageChildPercent = ageChild * percentChild

		if self.dlg.ui.chkloadDAdult.isChecked():
		   for feature in popFloodLayer.getFeatures():
			adult = feature['AGE_O_18']
			ageAdult = ageAdult + adult
			ageAdultPercent = ageAdult * percentAdult
	
		timePerDay = 0	
   		drugNameList.append(d2)
   		drugPriceList.append(r2)
   		doseChildrenList.append(c2)
   		doseAdultList.append(a2)
		timeCount = self.dlg.ui.txtTime.text()
		timePerDay = 24.0 / float(timeCount)
		CountNumberOfDays = self.dlg.ui.txtNoOfDays.text()
		numberOfDays = float(CountNumberOfDays)
		priceForOneTime = (ageAdultPercent * float(r1) * float(c1)) + (ageChildPercent * float(r1) * float(a1))#((100 * float(s)) #* float(c) ) + (150 * float(s) * float(a) )
		priceForOne = priceForOneTime * timePerDay * numberOfDays
		drugPrice.append(str(priceForOne))
	
		
	
		for x in range(0, len(drugNameList)):
		
	   		
			self.dlg.ui.txtAdQ3.setText(str(doseAdultListb[x]))
			self.dlg.ui.txtChQ3.setText(str(doseChildrenListb[x]))
			aduktQty = self.dlg.ui.txtAdQ3.text()
			childQty = self.dlg.ui.txtChQ3.text()
			totQty = (float(aduktQty) * float(ageAdultPercent) ) + (float(childQty) * float(ageChildPercent) )
			self.dlg.ui.txtTotQty3.setText(str(totQty))

    def calcQty3(self):
		priceForOne = 0
		
		global percentChild 
		percentChild = float(self.dlg.ui.cmbDChild.currentText())
		global percentAdult
		percentAdult = float(self.dlg.ui.cmbDAdult.currentText())
	
		
		df2 = self.dlg.ui.txtDrug4.text()
		d2 = str(df2)
		
		rd2 = self.dlg.ui.txtUP4.text()
		r2 = str(rd2)
		
		cf2 = self.dlg.ui.txtChildDose4.text()
		c2 = str(cf2)
		
		af2 = self.dlg.ui.txtAdultDose4.text()
		a2 = str(af2)
		
		ageChild = 0
		ageAdult = 0
		ageChildPercent = 0
		ageAdultPercent = 0
		popFloodLayer = self.iface.activeLayer()
		if self.dlg.ui.chkloadDChild.isChecked():
		   for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChild = ageChild + child
			ageChildPercent = ageChild * percentChild

		if self.dlg.ui.chkloadDAdult.isChecked():
		   for feature in popFloodLayer.getFeatures():
			adult = feature['AGE_O_18']
			ageAdult = ageAdult + adult
			ageAdultPercent = ageAdult * percentAdult
	
		timePerDay = 0	
   		drugNameList.append(d2)
   		drugPriceList.append(r2)
   		doseChildrenList.append(c2)
   		doseAdultList.append(a2)
		timeCount = self.dlg.ui.txtTime.text()
		timePerDay = 24.0 / float(timeCount)
		CountNumberOfDays = self.dlg.ui.txtNoOfDays.text()
		numberOfDays = float(CountNumberOfDays)
		priceForOneTime = (ageAdultPercent * float(r1) * float(c1)) + (ageChildPercent * float(r1) * float(a1))#((100 * float(s)) #* float(c) ) + (150 * float(s) * float(a) )
		priceForOne = priceForOneTime * timePerDay * numberOfDays
		drugPrice.append(str(priceForOne))
	
		
	
		for x in range(0, len(drugNameList)):
		
	   		
			self.dlg.ui.txtAdQ4.setText(str(doseAdultListc[x]))
			self.dlg.ui.txtChQ4.setText(str(doseChildrenListc[x]))
			aduktQty = self.dlg.ui.txtAdQ4.text()
			childQty = self.dlg.ui.txtChQ4.text()
			totQty = (float(aduktQty) * float(ageAdultPercent) ) + (float(childQty) * float(ageChildPercent) )
			self.dlg.ui.txtTotQty4.setText(str(totQty))


    def viewDetailsDrug2(self):

		style = getSampleStyleSheet()	
		pdf = SimpleDocTemplate("Medicinal Drugs Estimation - With Existing Details - FLOOgin Report.pdf")
		clBl = '<font color="blue">'
		clBls = '</font>'
		clR = '<font color="red">'
		clRs = '</font>'
		h2 = '<h1>'
		h2s = '</h1>'
		detailsBudget3.append( h2 + clR + "<b>Medicinal Drugs Estimation - FLOOgin Report </b>" + clRs + h2s )
		global floodLyrForBudRpt3

		crs = str(self.iface.activeLayer().crs().authid())
		now = datetime.datetime.now()
		date = now.strftime("%Y-%m-%d")
		time = now.strftime("%H:%M")

		detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " #+ clBl + str(floodLyrForBudRpt) + clBls
		detDateTime = "Generated on : " + date + " at " + time
		detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
		detailsBudget3.append(str(detHazard))
		detailsBudget3.append(str(detDateTime))
		detailsBudget3.append(str(detCrs))
		priceForOne = 0
		
		global percentChild 
		percentChild = float(self.dlg.ui.cmbDChild.currentText())
		global percentAdult
		percentAdult = float(self.dlg.ui.cmbDAdult.currentText())
	
		
		df2 = self.dlg.ui.txtDrug2.text()
		d2 = str(df2)
		
		rd2 = self.dlg.ui.txtUP2.text()
		r2 = str(rd2)
		
		cf2 = self.dlg.ui.txtChildDose2.text()
		c2 = str(cf2)
		
		af2 = self.dlg.ui.txtAdultDose2.text()
		a2 = str(af2)
		
		ageChild = 0
		ageAdult = 0
		ageChildPercent = 0
		ageAdultPercent = 0
		popFloodLayer = self.iface.activeLayer()
		if self.dlg.ui.chkloadDChild.isChecked():
		   for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChild = ageChild + child
			ageChildPercent = ageChild * percentChild

		if self.dlg.ui.chkloadDAdult.isChecked():
		   for feature in popFloodLayer.getFeatures():
			adult = feature['AGE_O_18']
			ageAdult = ageAdult + adult
			ageAdultPercent = ageAdult * percentAdult
	

		global storyBudget3
		storyBudget3 = []
		global drugReport3
		drugReport3 =[]
		global detailsBudget3
		detailsBudget3 = []

		timePerDay = 0
   		drugNameList.append(d2)
   		drugPriceList.append(r2)
   		doseChildrenList.append(c2)
   		doseAdultList.append(a2)
		timeCount = self.dlg.ui.txtTime.text()
		timeCount2 = self.dlg.ui.txtTime_2.text()
		timePerDay = 24.0 / float(timeCount)
		timePerDay2 = 24.0 / float(timeCount2)
		CountNumberOfDays = self.dlg.ui.txtNoOfDays.text()
		numberOfDays = float(CountNumberOfDays)
		priceForOneTime = (ageAdultPercent * float(r2) * float(c2)) + (ageChildPercent * float(r2) * float(a2))#((100 * float(s)) #* float(c) ) + (150 * float(s) * float(a) )
		priceForOneD = priceForOneTime * timePerDay * numberOfDays
		priceForTwoD = priceForOneTime * timePerDay2 * numberOfDays
		priceForOne = priceForOneD + priceForTwoD
		drugPrice.append(str(priceForOne))
		self.dlg.ui.textBrowser_2.clear()
	
		tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th width="90" align="left">Unit_Price</th><th width="90" align="left">Child_Qty</th><th width="90" align="left">Adult_Qty</th><th width="90" align="left">Price</th><</tr>'

		styles = getSampleStyleSheet()
		nm = Paragraph('''<b>NAME</b>''',styles["Normal"])
		tp = Paragraph('''<b>Unit Price</b>''',styles["Normal"])
		cs = Paragraph('''<b>Child Qty</b>''',styles["Normal"])
		md = Paragraph('''<b>Adult Qty</b>''',styles["Normal"])
		pd = Paragraph('''<b>Price</b>''',styles["Normal"])
		drugReport3.append( [ nm, tp, cs, md , pd ] )

		
		self.dlg.listDrugDetails(tb)
	
	
		for x in range(0, len(drugNameList)):
		
	   		self.dlg.listDrugDetails('<tr><td width="250">'+str(drugNameList[x])+'</td><td width="90">'+str(drugPriceList[x])+'</td><td width="90">'+str(doseChildrenList[x])+'</td><td width="90">'+str(doseAdultList[x])+'</td><td width="90">'+str(drugPrice[x])+'</td></tr>')
			drugReport3.append( [str(drugNameList[x]), str(drugPriceList[x]), str(doseChildrenList[x]), str(doseAdultList[x]),str(drugPrice[x]) ] )

			tbDrugEst3 = Table(drugReport3)
			storyBudget3.append( tbDrugEst3 ) 
			pdf.build(storyBudget3)

			self.dlg.ui.txtTot2.setText(str(drugPrice[x]))

			aduktQty2 = self.dlg.ui.txtAdQ2.text()
			childQty2 = self.dlg.ui.txtChQ2.text()
			totQty2 = (float(aduktQty2) * float(ageAdultPercent) ) + (float(childQty2) * float(ageChildPercent) )
			self.dlg.ui.txtTotQty2.setText(str(totQty2)) #txtTotQtyCount
			qtyCal2 = self.dlg.ui.txtTotQty2.text()
			qtyCal22 = str(qtyCal2)

			global qtyView
			qtyView = str(self.dlg.ui.cmbdiarrhea.currentText())
			#if disease == 'Bacterial Diarrhea' : 
      			global drugQtySize2
			drugQtySize2 = str(self.dlg.ui.cmbDrugSize.currentText())
			if drugQtySize2 == '500':
				qtyCalc = (float(qtyCal22) + float(qtyCal1))  / 500.0
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

			if drugQtySize2 == '250':
				qtyCalc = (float(qtyCal22) + float(qtyCal1)) / 250.0
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

			if drugQtySize2 == '100':
				qtyCalc = (float(qtyCal22) + float(qtyCal1)) / 100.0
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))
			
    
    def viewTotQty(self):
	global qtyView
	qtyView = str(self.dlg.ui.cmbdiarrhea.currentText())
	if disease == 'Bacterial Diarrhea' : 
		self.dlg.ui.txtTotQtyCount.text.clear()
		
		ageChild = 0
		ageAdult = 0
		ageChildPercent = 0
		ageAdultPercent = 0
		popFloodLayer = self.iface.activeLayer()
		if self.dlg.ui.chkloadDChild.isChecked():
		   for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChild = ageChild + child
			ageChildPercent = ageChild * percentChild

		if self.dlg.ui.chkloadDAdult.isChecked():
		   for feature in popFloodLayer.getFeatures():
			adult = feature['AGE_O_18']
			ageAdult = ageAdult + adult
			ageAdultPercent = ageAdult * percentAdult
	

		aduktQty2 = self.dlg.ui.txtAdQ2.text()
		childQty2 = self.dlg.ui.txtChQ2.text()
		totQty2 = (float(aduktQty2) * float(ageAdultPercent) ) + (float(childQty2) * float(ageChildPercent) )
		self.dlg.ui.txtTotQty2.setText(str(totQty2)) 
		qtyCal2 = self.dlg.ui.txtTotQty2.text()
		qtyCal22 = str(qtyCal2)

		global qtyView
		qtyView = str(self.dlg.ui.cmbdiarrhea.currentText())
		if disease == 'Bacterial Diarrhea' : 
      			 global drugQtySize2
			 drugQtySize2 = str(self.dlg.ui.cmbDrugSize.currentText())
			 if drugQtySize2 == '500':
				qtyCalc = (float(qtyCal22) + float(qtyCal1))  / 500.0
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

			 if drugQtySize2 == '250':
				qtyCalc = (float(qtyCal22) + float(qtyCal1)) / 250.0
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

			 if drugQtySize2 == '100':
				qtyCalc = (float(qtyCal22) + float(qtyCal1)) / 100.0
				self.dlg.ui.txtTotQtyCount.setText(str(qtyCalc))

    def viewDetailsDrug3(self):

		style = getSampleStyleSheet()	
		pdf = SimpleDocTemplate("Medicinal Drugs Estimation - With Existing Details - FLOOgin Report.pdf")
		clBl = '<font color="blue">'
		clBls = '</font>'
		clR = '<font color="red">'
		clRs = '</font>'
		h2 = '<h1>'
		h2s = '</h1>'
		detailsBudget4.append( h2 + clR + "<b>Medicinal Drugs Estimation - FLOOgin Report </b>" + clRs + h2s )
		global floodLyrForBudRpt4

		crs = str(self.iface.activeLayer().crs().authid())
		now = datetime.datetime.now()
		date = now.strftime("%Y-%m-%d")
		time = now.strftime("%H:%M")

		detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " #+ clBl + str(floodLyrForBudRpt) + clBls
		detDateTime = "Generated on : " + date + " at " + time
		detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
		detailsBudget4.append(str(detHazard))
		detailsBudget4.append(str(detDateTime))
		detailsBudget4.append(str(detCrs))

		priceForOne = 0
		
		global percentChild 
		percentChild = float(self.dlg.ui.cmbDChild.currentText())
		global percentAdult
		percentAdult = float(self.dlg.ui.cmbDAdult.currentText())
	
		
		df3 = self.dlg.ui.txtDrug3.text()
		d3 = str(df3)
		
		rd3 = self.dlg.ui.txtUP3.text()
		r3 = str(rd3)
		
		cf3 = self.dlg.ui.txtChildDose3.text()
		c3 = str(cf3)
		
		af3 = self.dlg.ui.txtAdultDose3.text()
		a3 = str(af3)
		
		ageChild = 0
		ageAdult = 0
		ageChildPercent = 0
		ageAdultPercent = 0
		popFloodLayer = self.iface.activeLayer()
		if self.dlg.ui.chkloadDChild.isChecked():
		   for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChild = ageChild + child
			ageChildPercent = ageChild * percentChild

		if self.dlg.ui.chkloadDAdult.isChecked():
		   for feature in popFloodLayer.getFeatures():
			adult = feature['AGE_O_18']
			ageAdult = ageAdult + adult
			ageAdultPercent = ageAdult * percentAdult

		global storyBudget4
		storyBudget4 = []
		global drugReport4
		drugReport4 =[]
		global detailsBudget4
		detailsBudget4 = []

	
		timePerDay = 0
   		drugNameList.append(d3)
   		drugPriceList.append(r3)
   		doseChildrenList.append(c3)
   		doseAdultList.append(a3)
		timeCount = self.dlg.ui.txtTime.text()
		timePerDay = 24.0 / float(timeCount)
		CountNumberOfDays = self.dlg.ui.txtNoOfDays.text()
		numberOfDays = float(CountNumberOfDays)
		priceForOneTime = (ageAdultPercent * float(r1) * float(c1)) + (ageChildPercent * float(r1) * float(a1))#((100 * float(s)) #* float(c) ) + (150 * float(s) * float(a) )
		priceForOne = priceForOneTime * timePerDay * numberOfDays
		drugPrice.append(str(priceForOne))
	
		self.dlg.ui.textBrowser_2.clear()
	
		tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th width="90" align="left">Unit_Price</th><th width="90" align="left">Child_Qty</th><th width="90" align="left">Adult_Qty</th><th width="90" align="left">Price</th><</tr>'

		styles = getSampleStyleSheet()
		nm = Paragraph('''<b>NAME</b>''',styles["Normal"])
		tp = Paragraph('''<b>Unit Price</b>''',styles["Normal"])
		cs = Paragraph('''<b>Child Qty</b>''',styles["Normal"])
		md = Paragraph('''<b>Adult Qty</b>''',styles["Normal"])
		pd = Paragraph('''<b>Price</b>''',styles["Normal"])
		drugReport4.append( [ nm, tp, cs, md , pd ] )
		
		self.dlg.listDrugDetails(tb)
	
	
		for x in range(0, len(drugNameList)):
		
	   		self.dlg.listDrugDetails('<tr><td width="250">'+str(drugNameList[x])+'</td><td width="90">'+str(drugPriceList[x])+'</td><td width="90">'+str(doseChildrenList[x])+'</td><td width="90">'+str(doseAdultList[x])+'</td><td width="90">'+str(drugPrice[x])+'</td></tr>')

			drugReport4.append( [str(drugNameList[x]), str(drugPriceList[x]), str(doseChildrenList[x]), str(doseAdultList[x]),str(drugPrice[x]) ] )

			tbDrugEst4 = Table(drugReport4)
			storyBudget4.append( tbDrugEst4 ) 
			pdf.build(storyBudget4)

			self.dlg.ui.txtTot3.setText(str(drugPrice[x]))

			

    def viewDetailsDrug4(self):

		style = getSampleStyleSheet()	
		pdf = SimpleDocTemplate("Medicinal Drugs Estimation - With Existing Details - FLOOgin Report.pdf")
		clBl = '<font color="blue">'
		clBls = '</font>'
		clR = '<font color="red">'
		clRs = '</font>'
		h2 = '<h1>'
		h2s = '</h1>'
		detailsBudget5.append( h2 + clR + "<b>Medicinal Drugs Estimation - FLOOgin Report </b>" + clRs + h2s )
		global floodLyrForBudRpt5

		crs = str(self.iface.activeLayer().crs().authid())
		now = datetime.datetime.now()
		date = now.strftime("%Y-%m-%d")
		time = now.strftime("%H:%M")

		detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " #+ clBl + str(floodLyrForBudRpt) + clBls
		detDateTime = "Generated on : " + date + " at " + time
		detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates"
	
		detailsBudget5.append(str(detHazard))
		detailsBudget5.append(str(detDateTime))
		detailsBudget5.append(str(detCrs))

		priceForOne = 0
		
		global percentChild 
		percentChild = float(self.dlg.ui.cmbDChild.currentText())
		global percentAdult
		percentAdult = float(self.dlg.ui.cmbDAdult.currentText())
	
		
		df4 = self.dlg.ui.txtDrug4.text()
		d4 = str(df4)
		
		rd4 = self.dlg.ui.txtUP4.text()
		r4 = str(rd4)
		
		cf4 = self.dlg.ui.txtChildDose4.text()
		c4 = str(cf4)
		
		af4 = self.dlg.ui.txtAdultDose4.text()
		a4 = str(af4)
		
		ageChild = 0
		ageAdult = 0
		ageChildPercent = 0
		ageAdultPercent = 0
		popFloodLayer = self.iface.activeLayer()
		if self.dlg.ui.chkloadDChild.isChecked():
		   for feature in popFloodLayer.getFeatures():
			child = feature['AGE_U_18']
			ageChild = ageChild + child
			ageChildPercent = ageChild * percentChild

		if self.dlg.ui.chkloadDAdult.isChecked():
		   for feature in popFloodLayer.getFeatures():
			adult = feature['AGE_O_18']
			ageAdult = ageAdult + adult
			ageAdultPercent = ageAdult * percentAdult

		global storyBudget5
		storyBudget5 = []
		global drugReport5
		drugReport5 =[]
		global detailsBudget5
		detailsBudget5 = []
	

   		drugNameList.append(d4)
   		drugPriceList.append(r4)
   		doseChildrenList.append(c4)
   		doseAdultList.append(a4)
		priceForOne = (ageAdultPercent * float(r4) * float(c4)) + (ageChildPercent * float(r4) * float(a4))#((100 * float(s)) #* float(c) ) + (150 * float(s) * float(a) )
		drugPrice.append(str(priceForOne))

		
	
		self.dlg.ui.textBrowser_2.clear()
	
		tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th width="90" align="left">Unit_Price</th><th width="90" align="left">Child_Qty (mg / pkts)</th><th width="90" align="left">Adult_Qty (mg / pkts) </th><th width="90" align="left">Price</th><</tr>'

		styles = getSampleStyleSheet()
		nm = Paragraph('''<b>NAME</b>''',styles["Normal"])
		tp = Paragraph('''<b>Unit Price</b>''',styles["Normal"])
		cs = Paragraph('''<b>Child Qty</b>''',styles["Normal"])
		md = Paragraph('''<b>Adult Qty</b>''',styles["Normal"])
		pd = Paragraph('''<b>Price</b>''',styles["Normal"])
		drugReport5.append( [ nm, tp, cs, md , pd ] )
		
		self.dlg.listDrugDetails(tb)
	
	
		for x in range(0, len(drugNameList)):
		
	   		self.dlg.listDrugDetails('<tr><td width="250">'+str(drugNameList[x])+'</td><td width="90">'+str(drugPriceList[x])+'</td><td width="90">'+str(doseChildrenList[x])+'</td><td width="90">'+str(doseAdultList[x])+'</td><td width="90">'+str(drugPrice[x])+'</td></tr>')

			#self.dlg.listDrugDetails('<tr><td width="250">'+'Rs'+'</td><td width="100">'+str(viewTotal)+'</td></tr>')
			drugReport5.append( [str(drugNameList[x]), str(drugPriceList[x]), str(doseChildrenList[x]), str(doseAdultList[x]),str(drugPrice[x]) ] )

			tbDrugEst5 = Table(drugReport5)
			storyBudget5.append( tbDrugEst5 ) 
			pdf.build(storyBudget5)

			self.dlg.ui.txtTot4.setText(str(drugPrice[x]))

	
   
		
    def countApprovedDrugTotal(self):
	

	global approvedTotalPrice
	approvedTotalPrice = 0
	price1 = 0
	price2 = 0
	price3 = 0
	price4 = 0
	

	
	approvedTotalPrice = float(self.dlg.ui.txtTot1.text()) + float(self.dlg.ui.txtTot2.text()) + float(self.dlg.ui.txtTot3.text()) + float(self.dlg.ui.txtTot4.text())
	self.dlg.ui.txtAllTota.setText(str(approvedTotalPrice))	

	self.dlg.ui.txtAllTota.setVisible(True)    
	self.dlg.ui.label_68.setVisible(True) #txtAllTota
	self.dlg.ui.lblCapSize.setVisible(True)
	#self.dlg.ui.lblmgSize.setVisible(True)

	viewTotal = float(self.dlg.ui.txtAllTota.text())
	viewTotalN = str(viewTotal)

	#viewTotQty = float(self.dlg.ui.txtAllTota.text())

	self.dlg.listDrugDetails('<tr><td width="250">'+'Total Budget value = '+'Rs: '+str(viewTotalN)+'</td></tr>')

	#self.dlg.listDrugDetails('<tr><td width="250">'+'Total str(viewTotal)+'</td></tr>')

	QMessageBox.information( self.iface.mainWindow(),"Info", "Saved at /home/Medicinal Drugs Estimation - With Existing Details - FLOOgin Report.pdf")
		
	
###### new bud

    def clearBudget(self):
       self.dlg.ui.textBrowser.clear()
       self.dlg.ui.lblTotBudget.clear()

    def clearBudget2(self):
       self.dlg.ui.textBrowser.clear()
       self.dlg.ui.lblTotBudget.clear()
    
		

   
 


   

################################ Givanthika ######################################################################################	
	

    def genMapForImage(self):
	global pointsForImage

	#messagebox
	colBl = '<font color="blue">'
	colBls = '</font>'	
	textToShow = "Make sure that map canvas is zoomed to the desired zoom level"
	textSub = colBl + " For more fine details, apply labelling for necessary layers (Layer Prperties->Labels) " + colBls
	msgBox = QtGui.QMessageBox()
 	msgBox.setText(str(textToShow))
 	msgBox.setInformativeText(str(textSub))
 	msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
	msgBox.setDefaultButton(QMessageBox.Save)
	msgBox.setWindowTitle("Save as image")
 	ret = msgBox.exec_();

	if (ret == msgBox.Save):
		tempLayer = "temporary_points"
		# create layer
		vl = QgsVectorLayer("Point?crs=epsg:4326", "temporary_points", "memory")
		pr = vl.dataProvider()
		# add fields
		vl.startEditing()
		pr.addAttributes( [ QgsField("name", QVariant.String) ] )
		# add a feature
		for i in range(len(pointsForImage)):
			print i
			fet = QgsFeature()
			fet.setGeometry( QgsGeometry.fromPoint( pointsForImage[i] ))
			fet.setAttributes([str(self.getPlaceDirNameMoreSpecific(pointsForImage[i]))])
			pr.addFeatures([fet])
		# update layer’s extent when new features have been added
		# because change of extent in provider is not propagated to the layer
		vl.updateExtents()
		vl.commitChanges()
		#verify layer craeted
		print "fields:", len(pr.fields())
		print "features:", pr.featureCount()
		f = QgsFeature()
		features = vl.getFeatures()
		for f in features:
			print "F:",f.id(), f.attributes(), f.geometry().asPoint()
		QgsMapLayerRegistry.instance().addMapLayer(vl)

		#change color
		symbols = vl.rendererV2().symbols()
		symbol = symbols[0]
		symbol.setColor(QtGui.QColor.fromRgb(0,170,0))
		self.canvas.refresh() 
		self.iface.legendInterface().refreshLayerSymbology(vl)

		legend = self.iface.legendInterface()
		allLayersListNew = self.iface.legendInterface().layers()
	 	for getLayerNew in allLayersListNew:
			print "in"
			if str(getLayerNew.name()) == str(tempLayer):
				print "temp"
				legend.setLayerVisible(getLayerNew, True)
			elif str(getLayerNew.name()) == 'Roads_safe':
				print "safe"
				legend.setLayerVisible(getLayerNew, True)
				self.labell()
				self.labell()
			else:
				print "other"
				legend.setLayerVisible(getLayerNew, False)
		global filePath
		imgPath = str(filePath) + 'FLOOgin_path.png'
		self.canvas.saveAsImage('FLOOgin_path.png', None, 'PNG')
		src = 'FLOOgin_path.png'
		dst = str(filePath)
		self.copyFile(src,dst)
		colB = '<font color="blue">'
		colBs = '</font>'	
		textToShow = "Image Saved Successfully" 
		textSub = "Saved in " + colB + str(filePath) + colBs +" as FLOOgin_path.png "
		msgBox = QtGui.QMessageBox()
	 	msgBox.setText(str(textToShow))
	 	msgBox.setInformativeText(str(textSub))
	 	msgBox.setStandardButtons(QMessageBox.Ok)
		msgBox.setWindowTitle("Generate Image File")
	 	ret = msgBox.exec_();

		legendd = self.iface.legendInterface()
		allLayersListNeww = self.iface.legendInterface().layers()
	 	for getLayerNeww in allLayersListNeww:
			print "in"
			if str(getLayerNeww.name()) == str(tempLayer):
				print "tempp"
				legendd.setLayerVisible(getLayerNeww, False)
			elif str(getLayerNew.name()) == 'Roads_safe':
				print "safe"
				legend.setLayerVisible(getLayerNew, True)
				self.Hidelabell(getLayerNew)
			else:
				print "otherr"
				legendd.setLayerVisible(getLayerNeww, True)

	elif (ret == msgBox.Discard):
		print "Discard"
	elif (ret == msgBox.Cancel):
		print "Cancel"
	else:
		print "None"	
	#messagebox


    def genBRoadsImage(self):
	global blockedRoadLayer
	#change color
	symbols = blockedRoadLayer.rendererV2().symbols()
	symbol = symbols[0]
	symbol.setColor(QtGui.QColor.fromRgb(0,0,255))
	self.canvas.refresh() 
	self.iface.legendInterface().refreshLayerSymbology(blockedRoadLayer)

	legend = self.iface.legendInterface()
	allLayersListNew = self.iface.legendInterface().layers()
	for getLayerNew in allLayersListNew:
		print "in"
		if str(getLayerNew.name()) == str(blockedRoadLayer.name()):
			print "blocked"
			legend.setLayerVisible(getLayerNew, True)
			self.label(getLayerNew)
			self.label(getLayerNew)				
		else:
			print "other"
			legend.setLayerVisible(getLayerNew, False)
		
	self.canvas.saveAsImage('Blocked_Roads.png', None, 'PNG')

	legendd = self.iface.legendInterface()
	allLayersListNeww = self.iface.legendInterface().layers()
	for getLayerNeww in allLayersListNeww:
		print "in"
		if str(getLayerNeww.name()) == str(blockedRoadLayer.name()):
			print "blocked"
			legendd.setLayerVisible(getLayerNeww, False)
		else:
			print "otherr"
			legendd.setLayerVisible(getLayerNeww, True)



    def label(self,layer):
	palyrr = QgsPalLayerSettings()
	palyrr.readFromLayer(layer)
	palyrr.enabled = False
	palyrr.fieldName = 'name'
	palyrr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'08','')
	palyrr.placement = QgsPalLayerSettings.Line
	palyrr.writeToLayer(layer)
	layer.commitChanges()
	#palyrr.enabled = False
	self.iface.mapCanvas().refresh()
	palyrr = QgsPalLayerSettings()
	palyrr.readFromLayer(layer)
	palyrr.enabled = True
	palyrr.fieldName = 'name'
	palyrr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'08','')
	palyrr.placement = QgsPalLayerSettings.Line
	palyrr.writeToLayer(layer)
	layer.commitChanges()
	#palyrr.enabled = False
	self.iface.mapCanvas().refresh()

    def labell(self):
	layer = self.iface.mapCanvas().currentLayer()
	palyrr = QgsPalLayerSettings()
	palyrr.readFromLayer(layer)
	palyrr.enabled = False
	palyrr.fieldName = 'name'
	palyrr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'08','')
	palyrr.placement = QgsPalLayerSettings.Line
	palyrr.writeToLayer(layer)
	layer.commitChanges()
	#palyrr.enabled = False
	self.iface.mapCanvas().refresh()
	##layer = self.iface.mapCanvas().currentLayer()
	palyrr = QgsPalLayerSettings()
	palyrr.readFromLayer(layer)
	palyrr.enabled = True
	palyrr.fieldName = 'name'
	palyrr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'08','')
	palyrr.placement = QgsPalLayerSettings.Line
	palyrr.writeToLayer(layer)
	layer.commitChanges()
	#palyrr.enabled = False
	self.iface.mapCanvas().refresh()


    def Hidelabell(self,layer):
	palyrr = QgsPalLayerSettings()
	palyrr.readFromLayer(layer)
	palyrr.enabled = False
	palyrr.fieldName = 'name'
	palyrr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'08','')
	palyrr.writeToLayer(layer)
	layer.commitChanges()
	#palyrr.enabled = False
	self.iface.mapCanvas().refresh()



    def nextOne(self):
	self.dlg.ui.tbwAltRoad.setCurrentIndex(1)

    def nextTwo(self):
	self.dlg.ui.tbwAltRoad.setCurrentIndex(2)

    def nextThree(self):
	self.labelPos.clear()
	global stopPlaceDir
	stopPlaceDir = 0	
	self.dlg.ui.tbwAltRoad.setCurrentIndex(3)

    def stopShowPathOnMap(self):
	self.labelPos.clear()
	global stopPlaceDir
	stopPlaceDir = 0	


    def roadLayerGlanceIndexChanged(self):
	try:
		global roadLayerGot 		
		roadLayerSelected = self.dlg.ui.cmbRoadLayerGlance.currentText()	
		roadLayerGot = self.getLayerByName( roadLayerSelected )
		fieldNameRoad = self.getFieldName( roadLayerGot )
		self.dlg.ui.cmbSelectRoadGlance.clear()
		for feature in roadLayerGot.getFeatures():						
			name = feature[fieldNameRoad]
			if str(name) != 'NULL':
				self.dlg.ui.cmbSelectRoadGlance.addItem( name )
	except:
		e = sys.exc_info()[0]
		print e



    def atGlnaceRoads(self):
	global roadLayerGot
	roadSelected = self.dlg.ui.cmbSelectRoadGlance.currentText()
	fieldNameRoad = self.getFieldName( roadLayerGot )							
	for feature in roadLayerGot.getFeatures():						
		name = feature[fieldNameRoad]
		geom = feature.geometry()
		if str(name) != 'NULL':
			if str(name) == str(roadSelected): 
				fid=feature.id()
				osmId = feature['osm_id']
				classs = feature['ref']
				typee = feature['type']
				oneway = feature['oneway']
				bridge = feature['bridge']
				tunnel = feature['tunnel']
	if int(str(oneway)) == 1:
		self.dlg.ui.lblGlanceWay.setText('Oneway')
		self.dlg.ui.lblOnewayYes.setVisible(True)
		self.dlg.ui.lblOnewayNo.setVisible(False)
	else:
		self.dlg.ui.lblGlanceWay.setText('Twoway')
		self.dlg.ui.lblOnewayYes.setVisible(True)
		self.dlg.ui.lblOnewayNo.setVisible(False)

	if int(str(bridge)) == 1:
		self.dlg.ui.lblBridgeYes.setVisible(True)
		self.dlg.ui.lblBridgeNo.setVisible(False)
	else:
		self.dlg.ui.lblBridgeNo.setVisible(True)
		self.dlg.ui.lblBridgeYes.setVisible(False)

	if int(str(tunnel)) == 1:
		self.dlg.ui.lblTunnelYes.setVisible(True)
		self.dlg.ui.lblTunnelNo.setVisible(False)
	else:
		self.dlg.ui.lblTunnelNo.setVisible(True)
		self.dlg.ui.lblTunnelYes.setVisible(False)

	if str(typee) == 'NULL':
		typee = 'Unknown'
	if str(classs) == 'NULL':
		classs = 'Unknown'

	self.dlg.ui.lblOsmIdGlance.setVisible(True)
	self.dlg.ui.lblClassGlance.setVisible(True)
	self.dlg.ui.lblTypeGlance.setVisible(True)	
	self.dlg.ui.lblOsmIdGlance.setText(osmId)
	self.dlg.ui.lblClassGlance.setText(classs)
	self.dlg.ui.lblTypeGlance.setText(typee)	


    def atGlnaceRoadsReset(self):
	self.dlg.ui.lblOsmIdGlance.setText('Osm ID')
	self.dlg.ui.lblClassGlance.setText('Class')
	self.dlg.ui.lblTypeGlance.setText('Type')
	self.dlg.ui.lblGlanceWay.setText('Oneway')	
	self.dlg.ui.lblOnewayYes.setVisible(False)
	self.dlg.ui.lblOnewayNo.setVisible(False)
	self.dlg.ui.lblBridgeYes.setVisible(False)
	self.dlg.ui.lblBridgeNo.setVisible(False)
	self.dlg.ui.lblTunnelYes.setVisible(False)
	self.dlg.ui.lblTunnelNo.setVisible(False)
	self.dlg.ui.lblOsmIdGlance.setVisible(False)
	self.dlg.ui.lblClassGlance.setVisible(False)
	self.dlg.ui.lblTypeGlance.setVisible(False)	
	self.dlg.ui.cmbRoadLayerGlance.clear()
	self.dlg.ui.cmbSelectRoadGlance.clear()
	allLayersLoaded = self.canvas.layers()
 	for SelLayer in allLayersLoaded:	
		self.dlg.ui.cmbRoadLayerGlance.addItem(SelLayer.name())
	#drive
	#drive = GoogleDrive(gauth) # Create GoogleDrive instance with authenticated GoogleAuth instance

	#file1 = drive.CreateFile({'title': 'Hello.txt'}) # Create GoogleDriveFile instance with title 'Hello.txt'
	#file1.Upload() # Upload it
	#print 'title: %s, id: %s' % (file1['title'], file1['id']) # title: Hello.txt, id: {{FILE_ID}}

    def atGlnaceRoadsRefresh(self):
	self.dlg.ui.cmbRoadLayerGlance.clear()
	allLayersLoaded = self.canvas.layers()
 	for SelLayer in allLayersLoaded:	
		self.dlg.ui.cmbRoadLayerGlance.addItem(SelLayer.name())

	############################
	#self.generateAudioDirections()

	#testing - directions
	#mapService = GoogleMaps()
	#directions = mapService.directions('Neboda bus stop','Panadura Hospital')
	#for step in directions['Directions']['Routes'][0]['Steps']:
		#print self.strip_tags(step['descriptionHtml'])
	
	#with open('directions.txt','w')	as f:
		#for step in directions['Directions']['Routes'][0]['Steps']:
			#f.write(self.strip_tags(step['descriptionHtml'] + '\r\n'))

	#testing - directions
	
	#testing
	#style = getSampleStyleSheet()	
	#pdf = SimpleDocTemplate("Test Report.pdf")
	#drawing = Drawing(400, 200)
	#data = [(13, 5, 20, 22, 37, 45, 19, 4)]
	#bc = VerticalBarChart()
	#bc.x = 50
	#bc.y = 50
	#bc.height = 175
	#bc.width = 350
	#bc.data = data
	#bc.strokeColor = colors.black
	#bc.valueAxis.valueMin = 0
	#bc.valueAxis.valueMax = 50
	#bc.valueAxis.valueStep = 10
	#bc.categoryAxis.labels.boxAnchor = 'ne'
	#bc.categoryAxis.labels.dx = 8
	#bc.categoryAxis.labels.dy = -2
	#bc.categoryAxis.labels.angle = 30
	#bc.categoryAxis.categoryNames = ['Jan-99','Feb-99','Mar-99','Apr-99','May-99','Jun-99','Jul-99','Aug-99']
	#drawing.add(bc)
	#pdf.build()
	#the_canvas = canvas.Canvas("outputGr.pdf")
	#renderPDF.draw(drawing, the_canvas, 0, 600)
	#the_canvas.showPage()
	# the_canvas.save()

	# pie chart
	#d = Drawing(200, 100)
	#pc = Pie()
	#pc.x = 65
	#pc.y = 15
	#pc.width = 70
	#pc.height = 70
	#pc.data = [10,20,30,40,50,60]
	#pc.labels = ['a','b','c','d','e','f']
	#pc.slices.strokeWidth=0.5
	#pc.slices[3].popout = 10
	#pc.slices[3].strokeWidth = 2
	#pc.slices[3].strokeDashArray = [2,2]
	#pc.slices[3].labelRadius = 1.75
	#pc.slices[3].fontColor = colors.red
	#d.add(pc)
	#renderPDF.draw(d, the_canvas, 0, 0)
	#the_canvas.showPage()
	#the_canvas.save()

	#testing
	#layer = self.canvas.currentLayer()
	#palyr = QgsPalLayerSettings()
	#palyr.readFromLayer(layer)
	#palyr.enabled = True #False
	#palyr.fieldName = 'name'
	#palyr.placement = QgsPalLayerSettings.OverPoint
	#palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
	#  palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
	#palyr.writeToLayer(layer)
	#self.iface.mapCanvas().refresh()

	# create layer
	#vl = QgsVectorLayer("Point", "temporary_points", "memory")
	#pr = vl.dataProvider()
	# add fields
	#vl.startEditing()
	#pr.addAttributes( [ QgsField("name", QVariant.String) ] )
	# add a feature
	#fet = QgsFeature()
	#fet.setGeometry( QgsGeometry.fromPoint(QgsPoint(80.0627,6.615)) )
	#fet.setAttributes(["Johny"])
	#pr.addFeatures([fet])
	# update layer’s extent when new features have been added
	# because change of extent in provider is not propagated to the layer
	#vl.updateExtents()
	#vl.commitChanges()
	#verify layer craeted
	#print "fields:", len(pr.fields())
	#print "features:", pr.featureCount()
	#f = QgsFeature()
	#features = vl.getFeatures()
	#for f in features:
		#print "F:",f.id(), f.attributes(), f.geometry().asPoint()
	#QgsMapLayerRegistry.instance().addMapLayer(vl)

	#layer = vl
	#palyr = QgsPalLayerSettings()
	#palyr.readFromLayer(layer)
	#palyr.enabled = True #False
	#palyr.fieldName = 'name'
	#palyr.placement = QgsPalLayerSettings.OverPoint
	#palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'20','')
	#palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
	#palyr.writeToLayer(layer)
	#self.iface.mapCanvas().refresh()



	#self.dlgEmailR.show()
	#self.dlgEmailR.exec_()

	#root = Tk()	
	#filename = askopenfilename(parent = root)	
	#f = open(filename, "r")#'/home/kasun/Alternative Route Finder-FLOOgin Report.pdf', "r") 
	#return f.read()
	#webbrowser.open(r'file:///home/kasun/Alternative Route Finder-FLOOgin Report.pdf') 

	#movie = QtGui.QMovie(":/plugins/floogin/loading1.gif")
	#self.dlg.ui.lblLoading.setMovie(movie)
	#movie.start()

    def strip_tags(self,html):
    	s = MLStripper()
    	s.feed(html)
    	return s.get_data()



    def refreshRoadLayer(self):
	self.dlg.ui.cboRoadLayer.clear()
	allLayersLoadedd = self.canvas.layers()
 	for SelLayerr in allLayersLoadedd:	
		self.dlg.ui.cboRoadLayer.addItem(SelLayerr.name())		
	
    def refreshFloodLayer(self):
	self.dlg.ui.cboFloodLayer.clear()
	allLayersLoadedd = self.canvas.layers()
 	for SelLayerr in allLayersLoadedd:	
		self.dlg.ui.cboFloodLayer.addItem(SelLayerr.name())		


    def refreshLabellingLayers(self):
	self.dlg.ui.cmbLayerLabelling.clear()
	allLayersLoadedd = self.canvas.layers()
 	for SelLayerr in allLayersLoadedd:	
		self.dlg.ui.cmbLayerLabelling.addItem(SelLayerr.name())		
	

    def showLabellingFeatures(self):
	global layerLbl
	global showField
	#global palyr
	layer = self.dlg.ui.cmbLayerLabelling.currentText()
	layerLbl = self.getLayerByName(layer)
	fieldN = self.dlg.ui.cmbFieldLabelling.currentText()
	showField = str(fieldN) 
	palyr = QgsPalLayerSettings()
	palyr.readFromLayer(layerLbl)
	palyr.enabled = True #False
	palyr.fieldName = showField
	palyr.placement = QgsPalLayerSettings.OverPoint
	palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
	#palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
	palyr.writeToLayer(layerLbl)
	self.canvas.refresh()
		
    def hideLabellingFeatures(self):
	global layerLbl
	global showField
	global palyr
	try:
		palyr = QgsPalLayerSettings()
		palyr.readFromLayer(layerLbl)
		palyr.enabled = False
		palyr.fieldName = showField
		palyr.placement = QgsPalLayerSettings.OverPoint
		palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
		# palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
		palyr.writeToLayer(layerLbl)
		self.canvas.refresh()
	except:
		print "donee"
		

    def helpDialogStart(self):
	# show the dialog
        self.dlgHelp.show()
	self.dlgHelp.uiHelp.tbwRoad.setCurrentIndex(0)
        # Run the dialog event loop
        self.dlgHelp.exec_()

    def helpDialogRoute(self):
	# show the dialog
        self.dlgHelp.show()
	self.dlgHelp.uiHelp.tbwRoad.setCurrentIndex(1)
        # Run the dialog event loop
        self.dlgHelp.exec_()

    def helpDialogDirec(self):
	# show the dialog
        self.dlgHelp.show()
	self.dlgHelp.uiHelp.tbwRoad.setCurrentIndex(2)
        # Run the dialog event loop
        self.dlgHelp.exec_()

    def helpDialogBlock(self):
	# show the dialog
        self.dlgHelp.show()
	self.dlgHelp.uiHelp.tbwRoad.setCurrentIndex(3)
        # Run the dialog event loop
        self.dlgHelp.exec_()

    def helpDialogBlockCat(self):
	# show the dialog
        self.dlgHelp.show()
	self.dlgHelp.uiHelp.tbwRoad.setCurrentIndex(3)
        # Run the dialog event loop
        self.dlgHelp.exec_()

    def helpDialogAdminAll(self):
	# show the dialog
        self.dlgHelp.show()
	self.dlgHelp.uiHelp.tbwRoad.setCurrentIndex(3)
        # Run the dialog event loop
        self.dlgHelp.exec_()

    def helpDialogAdminCat(self):
	# show the dialog
        self.dlgHelp.show()
	self.dlgHelp.uiHelp.tbwRoad.setCurrentIndex(3)
        # Run the dialog event loop
        self.dlgHelp.exec_()	


    def helpDialogClose(self):
	self.dlgHelp.hide()


    def identifyBlockedRoads(self):
	global rdPath
	global fdPath
	global bRoadsForReport
	global bRoadsSum
	global bRoadsfCount
	global layer_path_haz
	global layer_path_rd
	global bRoadPath
	global blockedRoadLayer
	roadType = []
	if rdPath == '':
		rdPath = layer_path_rd
	if fdPath == '':
		fdPath = layer_path_haz
	bRoadsForReport = []
	bRoadsSum = []
	output = os.path.splitext(rdPath)[0]
	output += '_Blocked.shp'
	bRoadPath = output
	outputFile = 'blockedRoads'
	## outputFile = 'KalutaraRoads_Blocked'
	## processing.runandload("qgis:difference", rdPath, fdPath, output)
	processing.runalg("qgis:intersection", rdPath, fdPath, output)
	wb = QgsVectorLayer(output, outputFile, 'ogr')
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
	else:
		print "No layer found"
	#active new layer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		print "ok1"
		if str(getLayerNew.name()) == str(outputFile):
			legend.setLayerVisible(getLayerNew, True)
	

	allLayersListNeww = self.canvas.layers()
 	for getLayerNeww in allLayersListNeww:
		print "okkkk"
		if str(getLayerNeww.name()) == str(outputFile):
			blockedRoadLayer = self.getLayerByName( getLayerNeww.name() )
			#print "okkkk"

	try: 
		fieldNameRoad = self.getFieldName( blockedRoadLayer )
		fieldRoadType = self.getFieldRoadType( blockedRoadLayer )
		fieldRoadRef = self.getFieldRoadRef( blockedRoadLayer )
		fieldRoadOneway = self.getFieldRoadOneway( blockedRoadLayer )
		fieldRoadBridge = self.getFieldRoadBridge( blockedRoadLayer )
		fieldRoadTunnel = self.getFieldRoadTunnel( blockedRoadLayer )
		self.dlg.ui.txtBlockedRoads.clear()
		b = '<b>'
		bs = '</b>'
		#colHeads = b + 'Name     Type     Class     Oneway     Bridge     Tunnel ' + bs + '\n'
		colHeads = '<table style="width:300px"><tr><th width="200" align="left">Name</th><th></th><th width="100" align="left">Type</th><th></th><th width="80" align="left">Class</th><th></th><th width="60" align="left">Oneway</th><th></th><th width="50" align="left">Bridge</th><th></th><th width="60" align="left">Tunnel</th></tr>'
		self.dlg.ui.txtBlockedRoads.setText( colHeads )
		styles = getSampleStyleSheet()
		nm = Paragraph('''<b>NAME</b>''',styles["Normal"])
		tp = Paragraph('''<b>TYPE</b>''',styles["Normal"])
		cs = Paragraph('''<b>CLASS</b>''',styles["Normal"])
		md = Paragraph('''<b>MODE</b>''',styles["Normal"])
		bRoadsForReport.append( [ nm, tp, cs, md ] )
 		bRoadsfCount = 1
		roadLen = 0.0
		for feature in blockedRoadLayer.getFeatures():
			mode = ''
			geom = feature.geometry()
			length = geom.length()
			#print length
            		roadLen += length					
			name = feature[fieldNameRoad]
			typee = feature[fieldRoadType]
			roadType.append(typee)
			ref = feature[fieldRoadRef]		
			oneway = feature[fieldRoadOneway]
			bridge = feature[fieldRoadBridge]
			tunnel = feature[fieldRoadTunnel]
			if int(str(oneway)) == 1:
				oneway = 'Yes'
				mode = mode + 'Oneway '
			else:
				oneway = 'No'
				mode = mode + 'Twoway '

			if int(str(bridge)) == 1:
				bridge = 'Yes'
				mode = mode + 'Bridge '
			else:
				bridge = 'No'

			if int(str(tunnel)) == 1:
				tunnel = 'Yes'
				mode = mode + 'Tunnel '
			else:
				tunnel = 'No'

			#if str(name) == 'NULL': 
				#name = 'Unknown'
			if str(typee) == 'NULL':
				typee = 'Unknown'
			if str(ref) == 'NULL':
				ref = 'Unknown'

			#values = str(name) + '\t\t\t' + str(typee) + '\t' + str(ref) + '\t' + str(oneway) + '\t' + str(bridge) + '\t' + str(tunnel) + '\n'
			values = '<tr><td width="200">' + str(name) + '</td><td></td><td width="100">' + str(typee) + '</td><td></td><td width="80">' + str(ref) + '</td><td></td><td width="60">' + str(oneway) + '</td><td></td><td width="50">' + str(bridge) + '</td><td></td><td width="60">' + str(tunnel) + '</td></tr><tr></tr>'
			if str(name) != 'NULL':			
				self.dlg.ui.txtBlockedRoads.append( values )
				bRoadsForReport.append( [str(name), str(typee), str(ref), str(mode) ] )
				bRoadsfCount = bRoadsfCount + 1
		#self.dlg.ui.txtBlockedRoads.append( '</table>' )
		#deactive new layer
		legendd = self.iface.legendInterface()
		allLayersListNeww = self.canvas.layers()
 		for getLayerNeww in allLayersListNeww:
			if str(getLayerNeww.name()) == str(outputFile):
				legendd.setLayerVisible(getLayerNeww, False)
		print roadLen
		rdType = []
		rdType.append( roadType[0] )
		for typ in roadType:
			if not typ in rdType:
				rdType.append(typ)
		clBl = '<font color="blue">'
		clBls = '</font>'
		self.dlg.ui.txtBlockedRoads.append("\n")
		self.dlg.ui.txtBlockedRoads.append( clBl + "<b>Summary</b>" + clBls + "\n")
		#self.dlg.ui.txtBlockedRoads.append("\n")
		colHeadsSum = '<table style="width:300px"><tr><th width="100" align="left">Road Type</th><th></th><th width="100" align="left">Total Flooded</th><th></th><th width="100" align="left">Total Length(~m)</th></tr>'
		self.dlg.ui.txtBlockedRoads.append( colHeadsSum )
		typp = Paragraph('''<b>ROAD TYPE</b>''',styles["Normal"])
		tott = Paragraph('''<b>TOTAL FLOODED</b>''',styles["Normal"])
		totLen = Paragraph('''<b>TOTAL LENGTH(~M)</b>''',styles["Normal"])
		bRoadsSum.append( [ typp , tott , totLen ] )
		for rTyp in rdType:
			rCount = 0
			dis = 0.0
			for feature in blockedRoadLayer.getFeatures():
				typeR = feature[fieldRoadType]
				if typeR == rTyp:
					rCount += 1
					dist = feature.geometry().length()
					dis = dis + dist
					#line = feature.geometry().asPolyline()
    					#for seg_start, seg_end in self.pair(line):
        					#line_start = QgsPoint(seg_start)
        					#line_end = QgsPoint(seg_end)
						#dist = self.distance(line_start.x(), line_start.y(), line_end.x(), line_end.y())
						#dis = dis + dist
			#disRoundLen = round(dis, 4)			
			#lengthM = int(disRoundLen * 1000)
			lengthM = int(dis*111111) # 1degree ~= 111111 m	
			valuesSum = '<tr><td width="100">' + str(rTyp) + '</td><td></td><td width="100">' + str(rCount) + '</td><td></td><td width="100">' + str(lengthM) + '</td></tr>' 
			#rdTypCnt = '<tr><td width="150">Road Type : ' + str(rTyp) + '</td> <td>Total flooded : ' + str(rCount) + '</td> <td>Total Length(m) : ' + str(lengthM) + '</td></tr>'
			self.dlg.ui.txtBlockedRoads.append(valuesSum)
			bRoadsSum.append( [ str(rTyp), str(rCount), str(lengthM) ] )
	except:
		e = sys.exc_info()#[0]
		print e


    def pair(self,list):
    	'''Iterate over pairs in a list '''
    	for i in range(1, len(list)):
    	    yield list[i-1], list[i]	


    def clearBlockedRoads(self):
	self.dlg.ui.txtBlockedRoads.clear()


    #blocked roads categorized**********
    def refreshAdminisLyrs(self):
	self.dlg.ui.cmbAdminiLayer.clear()
	allLayersLoaded = self.canvas.layers()
 	for SelLayer in allLayersLoaded:		
		self.dlg.ui.cmbAdminiLayer.addItem(SelLayer.name())		

    def generateAdminisRoadsMap(self):
	global bRoadPath
	global unionBRdsAdLyr
	global bRoadsUnionPath
	adminlayer = self.dlg.ui.cmbAdminiLayer.currentText()
	allLayersList = self.canvas.layers()
 	for getLayer in allLayersList:
		if str(getLayer.name()) == str(adminlayer):
			adminPath = str(getLayer.source())

	output = os.path.splitext(bRoadPath)[0]
	output += '_Cat.shp'
	bRoadsUnionPath = output
	outputFile = 'blockedRoadsCat'
	processing.runalg("qgis:union", bRoadPath, adminPath, output)
	wb = QgsVectorLayer(output, outputFile, 'ogr')
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
	else:
		print "No layer found"
	#active new layer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		print "done1"
		if str(getLayerNew.name()) == str(outputFile):
			legend.setLayerVisible(getLayerNew, True)
	

	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		print "done2"
		if str(getLayerNew.name()) == str(outputFile):
			blockedRoadLayerCat = self.getLayerByName( getLayerNew.name() )
			unionBRdsAdLyr = blockedRoadLayerCat

	#deactive new layer
	legendd = self.iface.legendInterface()
	allLayersListNeww = self.canvas.layers()
 	for getLayerNeww in allLayersListNeww:
		if str(getLayerNeww.name()) == str(outputFile):
			legendd.setLayerVisible(getLayerNeww, False)

	
    def radioAllSelect(self, enabled):
	if enabled:
		print "All"
		global All
		All = "yes"
		##self.dlg.ui.txtBlockedRdsCat.clear()
		self.dlg.ui.lblProvince.setVisible(False)
		self.dlg.ui.cmbProvince.setVisible(False)
		self.dlg.ui.btnProvinceOk.setVisible(False)
		self.dlg.ui.lblDistrict.setVisible(False)
		self.dlg.ui.cmbDistrict.setVisible(False)
		self.dlg.ui.btnDistOk.setVisible(False)
		self.dlg.ui.lblDS.setVisible(False)
		self.dlg.ui.cmbDS.setVisible(False)
		self.dlg.ui.btnDSOk.setVisible(False)
		self.dlg.ui.lblGND.setVisible(False)
		self.dlg.ui.cmbGND.setVisible(False)
		self.dlg.ui.btnGNDOk.setVisible(False)
		self.dlg.ui.lblDSDesc.setVisible(False)
		self.dlg.ui.lblGNDDesc.setVisible(False)
		#visible      
		self.dlg.ui.lblSortByR.setVisible(True)
		self.dlg.ui.cmbSortByAdmin.setVisible(True)
		self.dlg.ui.rdAscSort.setVisible(True)
		self.dlg.ui.lblAsc.setVisible(True)
		self.dlg.ui.rdDescSort.setVisible(True)
		self.dlg.ui.lblDesc.setVisible(True)
		self.generateLayerForBRoads()	


    def radioCatSelect(self, enabled):
	global unionBRdsAdLyr
	#global prov
	prov = []
	#global prvnc
	#global prvncCount
	if enabled:
		global All
		All = "no"
		print "Cat"
		##self.dlg.ui.txtBlockedRdsCat.clear()
		#self.dlg.ui.cmbAdminiLayer.enabled(False)
		self.dlg.ui.lblProvince.setVisible(True)
		self.dlg.ui.cmbProvince.setVisible(True)
		self.dlg.ui.btnProvinceOk.setVisible(True)
		#self.dlg.ui.lblDistrict.setVisible(True)
		#self.dlg.ui.cmbDistrict.setVisible(True)
		#self.dlg.ui.lblDS.setVisible(True)
		#self.dlg.ui.cmbDS.setVisible(True)
		#self.dlg.ui.lblGND.setVisible(True)
		#self.dlg.ui.cmbGND.setVisible(True)
		#self.dlg.ui.lblDSDesc.setVisible(True)
		#self.dlg.ui.lblGNDDesc.setVisible(True)
		#invisible rdAll fields
		self.dlg.ui.lblSortByR.setVisible(False)
		self.dlg.ui.cmbSortByAdmin.setVisible(False)
		self.dlg.ui.rdAscSort.setVisible(False)
		self.dlg.ui.lblAsc.setVisible(False)
		self.dlg.ui.rdDescSort.setVisible(False)
		self.dlg.ui.lblDesc.setVisible(False)	

		self.dlg.ui.cmbProvince.clear()
		#self.dlg.ui.cmbDistrict.clear()
		#self.dlg.ui.cmbDS.clear()
		#self.dlg.ui.cmbGND.clear()
	
		fieldNameRoad = self.getFieldName( unionBRdsAdLyr )
		for feature in unionBRdsAdLyr.getFeatures():				
			rdName = feature[fieldNameRoad]
			if str(rdName) != 'NULL':
				province = feature['PROVINCE_N']
				#print province
				if str(province) != 'NULL':
					prov.append(province)
		prvnc = []
		prvncCount = 1
		prvnc.append( prov[0] )
		for nm in prov:
			if not nm in prvnc:
				prvnc.append(nm)
				#prvncCount = prvncCount + 1

		for p in prvnc:		
			self.dlg.ui.cmbProvince.addItem(str(p))


    def provinceIndexChanged(self):
	global unionBRdsAdLyr
	global provSelected
	#global dist
	#global distct
	#global distctCount
	dist = []
	self.dlg.ui.cmbDistrict.clear()	 
	prov = self.dlg.ui.cmbProvince.currentText()
	provSelected = prov
	fieldNameRoad = self.getFieldName( unionBRdsAdLyr )
	if str(prov) != 'Select Province':
		for feature in unionBRdsAdLyr.getFeatures():
			rdName = feature[fieldNameRoad]
			if str(rdName) != 'NULL':
				province = feature['PROVINCE_N']
				if str(province) == str(prov):
					district = feature['DISTRICT_N']
					dist.append(district)
		distct = []
		distctCount = 1
		distct.append(dist[0])
		for nm in dist:
			if not nm in distct:
				distct.append(nm)
				#distctCount = distctCount + 1
		
		for p in distct:		
			self.dlg.ui.cmbDistrict.addItem(str(p))

	self.dlg.ui.lblDistrict.setVisible(True)
	self.dlg.ui.cmbDistrict.setVisible(True)
	self.dlg.ui.btnDistOk.setVisible(True)
					
		
    def districtIndexChanged(self):
	global unionBRdsAdLyr
	global distSelected
	#global DS 
	DS = []
	#global dsdd
	#global dsddCount
	self.dlg.ui.cmbDS.clear()	 
	dis = self.dlg.ui.cmbDistrict.currentText()
	distSelected = dis
	fieldNameRoad = self.getFieldName( unionBRdsAdLyr )
	if str(dis) != 'Select District':
		for feature in unionBRdsAdLyr.getFeatures():
			rdName = feature[fieldNameRoad]
			if str(rdName) != 'NULL':
				province = feature['PROVINCE_N']
				if str(province) != 'NULL':
					diss = feature['DISTRICT_N']
					if str(diss) == str(dis):
						dsd = feature['DSD_N']
						DS.append(dsd)
		dsdd = []
		dsddCount = 1
		dsdd.append(DS[0])
		for nm in DS:
			if not nm in dsdd:
				dsdd.append(nm)
				#dsddCount = dsddCount + 1

		for p in dsdd:		
			self.dlg.ui.cmbDS.addItem(str(p))

	self.dlg.ui.lblDS.setVisible(True)
	self.dlg.ui.cmbDS.setVisible(True)
	self.dlg.ui.btnDSOk.setVisible(True)
	self.dlg.ui.lblDSDesc.setVisible(True)


	
    def dsIndexChanged(self):	
	global unionBRdsAdLyr
	global dsSelected
	#global DS 
	GND = []
	#global gn
	#global gnCount
	self.dlg.ui.cmbGND.clear()	 
	ds = self.dlg.ui.cmbDS.currentText()
	dsSelected = ds
	fieldNameRoad = self.getFieldName( unionBRdsAdLyr )
	if str(ds) != 'Select DS':
		for feature in unionBRdsAdLyr.getFeatures():
			rdName = feature[fieldNameRoad]
			if str(rdName) != 'NULL':
				province = feature['PROVINCE_N']
				if str(province) != 'NULL':
					dss = feature['DSD_N']
					if str(dss) == str(ds):
						gndd = feature['GND_N']
						GND.append(gndd)
		gn = []
		gnCount = 1
		gn.append(GND[0])
		for nm in GND:
			if not nm in gn:
				gn.append(nm)
				#gnCount = gnCount + 1

		for p in gn:		
			self.dlg.ui.cmbGND.addItem(str(p))

	self.dlg.ui.lblGND.setVisible(True)
	self.dlg.ui.cmbGND.setVisible(True)
	self.dlg.ui.lblGNDDesc.setVisible(True)
	self.dlg.ui.btnGNDOk.setVisible(True)


    def gndIndexChanged(self):
	global gndSelected
	gnd = self.dlg.ui.cmbGND.currentText()
	gndSelected = gnd


    def radioAscSort(self, enabled):
	if enabled:
		print "Asc"
		global asc
 		asc = "yes"


    def radioDescSort(self, enabled):
	if enabled:
   		print "Desc"
		global asc
 		asc = "no"


    def generateLayerForBRoads(self):
	global unionBRdsAdLyr
	caps = unionBRdsAdLyr.dataProvider().capabilities()
	for f in unionBRdsAdLyr.getFeatures():
		pr = f['PROVINCE_N']
		nm = f['name']
		if ((str(pr) == "NULL") or (str(nm) == "NULL")):
			if caps & QgsVectorDataProvider.DeleteFeatures:
				res = unionBRdsAdLyr.dataProvider().deleteFeatures([f.id()])

    def identifyBlockedRoadsCat(self):
	#self.generateLayerForBRoads()
	global unionBRdsAdLyr
	global provSelected
	global distSelected
	global dsSelected
	global gndSelected
	global asc
	global bRoadsUnionPath
	global bRoadsCatForReport
	global bRoadsCatSpeciForReport
	global prCountt
	global disCountt
	global gnName
	#bRoadsCatForReport = []
	#bRoadsCatSpeciForReport = []
	styles = getSampleStyleSheet()
	#prov = []
	#dist = []
	#DS = []
	#GND = []
	proName = []
	disName = []
	gndName = []
	global All
	if str(All) == "yes":
		for feature in unionBRdsAdLyr.getFeatures():
			prV = feature['PROVINCE_N']
			diS = feature['DISTRICT_N']
			gnD = feature['GND_N']
			proName.append(prV)
			disName.append(diS)
			gndName.append(gnD)
			

		prName = []
		prName.append( proName[0] )
		prCountt = 1
		for typ in proName:
			if not typ in prName:
				prName.append(typ)
				prCountt = prCountt + 1
		print str(prCountt)
				
		dsName = []
		dsName.append( disName[0] )
		disCountt = 1
		for typ in disName:
			if not typ in dsName:
				dsName.append(typ)
				disCountt = disCountt + 1
		print str(disCountt)

		gnName = []
		gnName.append( gndName[0] )
		gnCountt = 1
		for typ in gndName:
			if not typ in gnName:
				gnName.append(str(typ))
				gnCountt = gnCountt + 1
		print str(gnCountt)
		
		#fieldNameRoad = self.getFieldName( unionBRdsAdLyr )
		#fieldRoadType = self.getFieldRoadType( unionBRdsAdLyr )
		#self.dlg.ui.txtBlockedRdsCat.clear()
		#b = '<b>'
		#bs = '</b>'
		#colHeads = '<table style="width:300px"><tr><th width="200" align="left">Name</th><th></th><th width="100" align="left">Type</th><th></th><th width="80" align="left">Province</th><th></th><th width="80" align="left">District</th><th></th><th width="80" align="left">DS</th><th></th><th width="100" align="left">GND</th></tr>'
		#self.dlg.ui.txtBlockedRdsCat.setText( colHeads )
		#for feature in unionBRdsAdLyr.getFeatures():					
			#name = feature[fieldNameRoad]
			#typee = feature[fieldRoadType]
			#prov = feature['PROVINCE_N']		
			#dist = feature['DISTRICT_N']
			#ds = feature['DSD_N']
			#gnd = feature['GND_N']
			#if str(typee) == 'NULL':
				#typee = 'Unknown'

			#values = '<tr><td width="200">' + str(name) + '</td><td></td><td width="100">' + str(typee) + '</td><td></td><td width="80">' + str(prov) + '</td><td></td><td width="80">' + str(dist) + '</td><td></td><td width="80">' + str(ds) + '</td><td></td><td width="100">' + str(gnd) + '</td></tr><tr></tr>'
			#if str(name) != 'NULL' and str(prov) != 'NULL':			
				#self.dlg.ui.txtBlockedRdsCat.append( values )

		self.dlg.ui.txtBlockedRdsCat.clear()
		fieldNameRoad = self.getFieldName( unionBRdsAdLyr )
		fieldRoadType = self.getFieldRoadType( unionBRdsAdLyr )
		colHeads = '<table style="width:300px"><tr><th width="200" align="left">Name</th><th></th><th width="100" align="left">Type</th><th></th><th width="80" align="left">Province</th><th></th><th width="80" align="left">District</th><th></th><th width="80" align="left">DS</th><th></th><th width="100" align="left">GND</th></tr>'
		self.dlg.ui.txtBlockedRdsCat.setText( colHeads )
		#for report
		#styles = getSampleStyleSheet()
		nmm = Paragraph('''<b>NAME</b>''',styles["Normal"])
		tpp = Paragraph('''<b>TYPE</b>''',styles["Normal"])
		prr = Paragraph('''<b>PROVINCE</b>''',styles["Normal"])
		dii = Paragraph('''<b>DISTRICT</b>''',styles["Normal"])
		dss = Paragraph('''<b>DS</b>''',styles["Normal"])
		gnn = Paragraph('''<b>GND</b>''',styles["Normal"])
		#bRoadsCatForReport.append( [ nmm, tpp, prr, dii, dss, gnn ] )
		global sortBy
		sortBy = self.dlg.ui.cmbSortByAdmin.currentText()
		path = str(bRoadsUnionPath)
		if str(sortBy) == "Province":
			sortBy = "PROVINCE_N"
		if str(sortBy) == "District":
			sortBy = "DISTRICT_N"
		if str(sortBy) == "Divisional Secretariats":
			sortBy = "DSD_N"
		if str(sortBy) == "Grama Niladhari Admin. D.":
			sortBy = "GND_N"

		ID = str(sortBy) 
		datasource = ogr.Open(str(path)) #datasource
		print str(path)

		layer = datasource.GetLayer(0) # Import layer 0 --> only works with shapefiles
		layerName = str( layer.GetName() )# Save the Layersname first
		print str(layerName)

		if str(asc) == "yes":
			global bRoadsCatForReport
			#sortBy = self.dlg.ui.cmbSortByAdmin.currentText()
			#path = str(bRoadsUnionPath)
			#if str(sortBy) == "Province":
				#sortBy = "PROVINCE_N"
			#if str(sortBy) == "District":
				#sortBy = "DISTRICT_N"
			#if str(sortBy) == "Divisional Secretariats":
				#sortBy = "DSD_N"
			#if str(sortBy) == "Grama Niladhari Admin. D.":
				#sortBy = "GND_N"

			#ID = str(sortBy) 
			#datasource = ogr.Open(str(path)) #datasource
			#print str(path)

			#layer = datasource.GetLayer(0) # Import layer 0 --> only works with shapefiles
			#layerName = str( layer.GetName() )# Save the Layersname first
			#print str(layerName)
			del bRoadsCatForReport[:] #clear list
			bRoadsCatForReport.append( [ nmm, prr, dii, dss, gnn ] )
			#sql query
			layers = datasource.ExecuteSQL("SELECT * FROM %s ORDER BY %s'" % (layerName, ID) )
			#layers = datasource.ExecuteSQL("SELECT * FROM %s ORDER BY %s DESC'" % (layerName, ID) )

			try:
				for i in range(0,layers.GetFeatureCount()):
					feat = layers.GetFeature(i)
					name = feat.GetField(str(fieldNameRoad))
					typee = feat.GetField(str(fieldRoadType))
					prov = feat.GetField('PROVINCE_N')		
					dist = feat.GetField('DISTRICT_N')
					ds = feat.GetField('DSD_N')
					gnd = feat.GetField('GND_N')
					##if str(typee) == 'NULL' or str(typee) == 'None':
						##typee = 'Unknown'
					print feat.GetField(str(ID))
					#print str(name)
	
					#if (str(name) != 'NULL' or str(name) != 'None') and (str(prov) != 'NULL' or str(prov) != 'None'):	
					values = '<tr><td width="200">' + str(name) + '</td><td></td><td width="100">' + str(typee) + '</td><td></td><td width="80">' + str(prov) + '</td><td></td><td width="80">' + str(dist) + '</td><td></td><td width="80">' + str(ds) + '</td><td></td><td width="100">' + str(gnd) + '</td></tr><tr></tr>'
					##if (str(name) != 'NULL' or str(name) != 'None') and (str(prov) != 'NULL' or str(prov) != 'None'):			
					self.dlg.ui.txtBlockedRdsCat.append( values )
					bRoadsCatForReport.append( [ str(name), str(prov), str(dist), str(ds), str(gnd) ] )
			except:
				#if nothing to sort, all same
				if str(sortBy) == 'PROVINCE_N':
					if prCountt == 1:
						for feature in unionBRdsAdLyr.getFeatures():
							nameE = feature[fieldNameRoad]
							typeE = feature[fieldRoadType]
							provV = feature['PROVINCE_N']		
							distT = feature['DISTRICT_N']
							dsS = feature['DSD_N']
							gndD = feature['GND_N']
							values = '<tr><td width="200">' + str(nameE) + '</td><td></td><td width="100">' + str(typeE) + '</td><td></td><td width="80">' + str(provV) + '</td><td></td><td width="80">' + str(distT) + '</td><td></td><td width="80">' + str(dsS) + '</td><td></td><td width="100">' + str(gndD) + '</td></tr><tr></tr>'
							self.dlg.ui.txtBlockedRdsCat.append( values )
							bRoadsCatForReport.append( [ str(nameE), str(provV), str(distT), str(dsS), str(gndD) ] )

				elif str(sortBy) == "DISTRICT_N":
					if disCountt == 1:
						for feature in unionBRdsAdLyr.getFeatures():
							nameEE = feature[fieldNameRoad]
							typeEE = feature[fieldRoadType]
							provVV = feature['PROVINCE_N']		
							distTT = feature['DISTRICT_N']
							dsSS = feature['DSD_N']
							gndDD = feature['GND_N']
							values = '<tr><td width="200">' + str(nameEE) + '</td><td></td><td width="100">' + str(typeEE) + '</td><td></td><td width="80">' + str(provVV) + '</td><td></td><td width="80">' + str(distTT) + '</td><td></td><td width="80">' + str(dsSS) + '</td><td></td><td width="100">' + str(gndDD) + '</td></tr><tr></tr>'
							self.dlg.ui.txtBlockedRdsCat.append( values )
							bRoadsCatForReport.append( [ str(nameEE), str(provVV), str(distTT), str(dsSS), str(gndDD) ] )


				print "done1"


		if str(asc) == "no":
			global bRoadsCatForReport
			del bRoadsCatForReport[:] #clear list
			bRoadsCatForReport.append( [ nmm, prr, dii, dss, gnn ] )
			#sql query
			#layers = datasource.ExecuteSQL("SELECT * FROM %s ORDER BY %s'" % (layerName, ID) )
			layers = datasource.ExecuteSQL("SELECT * FROM %s ORDER BY %s DESC'" % (layerName, ID) )

			try:
				for i in range(0,layers.GetFeatureCount()):
					feat = layers.GetFeature(i)
					name = feat.GetField(str(fieldNameRoad))
					typee = feat.GetField(str(fieldRoadType))
					prov = feat.GetField('PROVINCE_N')		
					dist = feat.GetField('DISTRICT_N')
					ds = feat.GetField('DSD_N')
					gnd = feat.GetField('GND_N')
					#if str(typee) == 'NULL' or str(typee) == 'None':
						#typee = 'Unknown'
					print feat.GetField(str(ID))
	
					values = '<tr><td width="200">' + str(name) + '</td><td></td><td width="100">' + str(typee) + '</td><td></td><td width="80">' + str(prov) + '</td><td></td><td width="80">' + str(dist) + '</td><td></td><td width="80">' + str(ds) + '</td><td></td><td width="100">' + str(gnd) + '</td></tr><tr></tr>'
					#if (str(name) != 'NULL' or str(name) != 'None') and (str(prov) != 'NULL' or str(prov) != 'None'):				
					self.dlg.ui.txtBlockedRdsCat.append( values )
					bRoadsCatForReport.append( [ str(name), str(prov), str(dist), str(ds), str(gnd) ] )

			except:
				#if nothing to sort, all same
				if str(sortBy) == "PROVINCE_N":
					if prCountt == 1:
						for feature in unionBRdsAdLyr.getFeatures():
							nameE = feature[fieldNameRoad]
							typeE = feature[fieldRoadType]
							provV = feature['PROVINCE_N']		
							distT = feature['DISTRICT_N']
							dsS = feature['DSD_N']
							gndD = feature['GND_N']
							values = '<tr><td width="200">' + str(nameE) + '</td><td></td><td width="100">' + str(typeE) + '</td><td></td><td width="80">' + str(provV) + '</td><td></td><td width="80">' + str(distT) + '</td><td></td><td width="80">' + str(dsS) + '</td><td></td><td width="100">' + str(gndD) + '</td></tr><tr></tr>'
							self.dlg.ui.txtBlockedRdsCat.append( values )
							bRoadsCatForReport.append( [ str(nameE), str(provV), str(distT), str(dsS), str(gndD) ] )

				elif str(sortBy) == "DISTRICT_N":
					if disCountt == 1:
						for feature in unionBRdsAdLyr.getFeatures():
							nameEE = feature[fieldNameRoad]
							typeEE = feature[fieldRoadType]
							provVV = feature['PROVINCE_N']		
							distTT = feature['DISTRICT_N']
							dsSS = feature['DSD_N']
							gndDD = feature['GND_N']
							values = '<tr><td width="200">' + str(nameEE) + '</td><td></td><td width="100">' + str(typeEE) + '</td><td></td><td width="80">' + str(provVV) + '</td><td></td><td width="80">' + str(distTT) + '</td><td></td><td width="80">' + str(dsSS) + '</td><td></td><td width="100">' + str(gndDD) + '</td></tr><tr></tr>'
							self.dlg.ui.txtBlockedRdsCat.append( values )
							bRoadsCatForReport.append( [ str(nameEE), str(provVV), str(distTT), str(dsSS), str(gndDD) ] )

				print "done2"



	if str(All) == "no":
		fieldNameRoad = self.getFieldName( unionBRdsAdLyr )
		fieldRoadType = self.getFieldRoadType( unionBRdsAdLyr )
		fieldRoadRef = self.getFieldRoadRef( unionBRdsAdLyr )
		fieldRoadOneway = self.getFieldRoadOneway( unionBRdsAdLyr )
		fieldRoadBridge = self.getFieldRoadBridge( unionBRdsAdLyr )
		fieldRoadTunnel = self.getFieldRoadTunnel( unionBRdsAdLyr )

		global bRoadsCatSpeciForReport		
		del bRoadsCatSpeciForReport[:] #clear list
		self.dlg.ui.txtBlockedRdsCat.clear()
		colHeads = '<table style="width:300px"><tr><th width="200" align="left">Name</th><th></th><th width="100" align="left">Type</th><th></th><th width="80" align="left">Class</th><th></th><th width="60" align="left">Oneway</th><th></th><th width="50" align="left">Bridge</th><th></th><th width="60" align="left">Tunnel</th></tr>'
		self.dlg.ui.txtBlockedRdsCat.setText( colHeads )
		#for report
		nme = Paragraph('''<b>NAME</b>''',styles["Normal"])
		tpe = Paragraph('''<b>TYPE</b>''',styles["Normal"])
		cls = Paragraph('''<b>CLASS</b>''',styles["Normal"])
		onw = Paragraph('''<b>ONEWAY</b>''',styles["Normal"])
		brg = Paragraph('''<b>BRIDGE</b>''',styles["Normal"])
		tnl = Paragraph('''<b>TUNNEL</b>''',styles["Normal"])
		bRoadsCatSpeciForReport.append( [ nme, tpe, cls, onw, brg, tnl ] )

		for feature in unionBRdsAdLyr.getFeatures():
			name = feature[fieldNameRoad]
			typee = feature[fieldRoadType]
			ref = feature[fieldRoadRef]		
			oneway = feature[fieldRoadOneway]
			bridge = feature[fieldRoadBridge]
			tunnel = feature[fieldRoadTunnel]
			prov = feature['PROVINCE_N']		
			dist = feature['DISTRICT_N']
			ds = feature['DSD_N']
			gnd = feature['GND_N']

			if str(name) != 'NULL':
				if str(prov) == str(provSelected) and str(dist) == str(distSelected) and str(ds) == str(dsSelected) and str(gnd) == str(gndSelected):							
					if int(str(oneway)) == 1:
						oneway = 'Yes'
						#mode = mode + 'Oneway '
					else:
						oneway = 'No'
						#mode = mode + 'Twoway '

					if int(str(bridge)) == 1:
						bridge = 'Yes'
						#mode = mode + 'Bridge '
					else:
						bridge = 'No'

					if int(str(tunnel)) == 1:
						tunnel = 'Yes'
						#mode = mode + 'Tunnel '
					else:
						tunnel = 'No'

					if str(typee) == 'NULL':
						typee = 'Unknown'
					if str(ref) == 'NULL':
						ref = 'Unknown'

					values = '<tr><td width="200">' + str(name) + '</td><td></td><td width="100">' + str(typee) + '</td><td></td><td width="80">' + str(ref) + '</td><td></td><td width="60">' + str(oneway) + '</td><td></td><td width="50">' + str(bridge) + '</td><td></td><td width="60">' + str(tunnel) + '</td></tr><tr></tr>'
					
					self.dlg.ui.txtBlockedRdsCat.append( values )
					bRoadsCatSpeciForReport.append( [ str(name), str(typee), str(ref), str(oneway), str(bridge), str(tunnel) ] )
	
	#self.blockedRoadsChart()


    def blockedRoadsChart(self):
	global unionBRdsAdLyr
	#global gnName
	global gnCnt
	global floodLyrForRpt
	#gnCnt = []
	#i = 0
	#while i < len(gnName):
		#noww = gnName[i]
		#gnCount = 0	
		#for feature in unionBRdsAdLyr.getFeatures():
			#gnDd = feature['GND_N']
			#if str(gnDd) == str(noww):
				#gnCount = gnCount + 1
		#gnCnt.append(gnCount)
		#i = i + 1

	#for ii in xrange(len(gnName)):
		#k = str(gnName[ii]) + " " + str(gnCnt[ii])
		#print str(k)

	##finding maximum
	#j = 0
	#maxim = 0
	#while j < len(gnCnt):
		#nw = gnCnt[j]		
		#if int(nw) >= int(gnCnt[maxim]):
			#maxim = j	
		#j = j + 1

	#highest = gnName[maxim]
	#print str(highest)

	#for feature in unionBRdsAdLyr.getFeatures():
		#gnDdD = feature['GND_N']
		#if str(gnDdD) == str(highest):
			#dsS = feature['DSD_N']
			#diS = feature['DISTRICT_N']
			#prV = feature['PROVINCE_N']

	#Find Unique GND names
	gndName = []
	for feature in unionBRdsAdLyr.getFeatures():			
		gnD = feature['GND_N']			
		gndName.append(gnD)
				
	gnNamee = []
	gnNamee.append( gndName[0] )
	for typ in gndName:
		if not typ in gnNamee:
			gnNamee.append(str(typ))

	

	#finding distances of roads blocked
	disRds = []
	for gn in gnNamee:
		#rCount = 0
		dis = 0.0
		for feature in unionBRdsAdLyr.getFeatures():
			gnDdDd = feature['GND_N']
			if gnDdDd == gn:
				#newly added
				dist = feature.geometry().length()			
				dis = dis + dist
				##rCount += 1
				#line = feature.geometry().asPolyline()
				#pp = "Line = " + str(line)
				#print str(pp)
    				#for seg_start, seg_end in self.pair(line):
					#print str(gnDdDd)
        				#line_start = QgsPoint(seg_start)
        				#line_end = QgsPoint(seg_end)
					#pp1 = "segs = " + str(line_start) + " " + str(line_end)
					#print str(pp1)
					#dist = self.distance(line_start.x(), line_start.y(), line_end.x(), line_end.y())
					#dis = dis + dist
		#disRoundLen = round(dis, 4)			
		#lengthM = int(disRoundLen * 1000)
		#disRds.append(lengthM)
		lengthM = int(dis*111111) # 1degree ~= 111111 m	
		disRds.append(lengthM)


	for iij in xrange(len(disRds)):
		kk = str(gnNamee[iij]) + " > " + str(disRds[iij])
		print str(kk)

	#finding maximum
	j = 0
	maxim = 0
	while j < len(disRds):
		nw = disRds[j]		
		if int(nw) >= int(disRds[maxim]):
			maxim = j	
		j = j + 1

	highest = gnNamee[maxim]
	print str(highest)
	disMax = disRds[maxim]

	for feature in unionBRdsAdLyr.getFeatures():
		gnDdD = feature['GND_N']
		if str(gnDdD) == str(highest):
			dsS = feature['DSD_N']
			diS = feature['DISTRICT_N']
			prV = feature['PROVINCE_N']



	drawing = Drawing(400, 200)
	#data = [(13, 5, 20, 22, 37, 45, 19, 4)]
	data = [(disRds)]
	bc = VerticalBarChart()
	bc.x = 50
	bc.y = 50
	bc.height = 375
	bc.width = 500
	bc.data = data
	bc.barSpacing = 5
	#bc.strokeColor = colors.white
	bc.bars.strokeWidth = 0.1
	bc.valueAxis.valueMin = 0
	bc.valueAxis.valueMax = 10000
	bc.valueAxis.valueStep = 500
	bc.categoryAxis.labels.boxAnchor = 'ne'
	bc.categoryAxis.labels.dx = -4
	bc.categoryAxis.labels.dy = -4
	bc.categoryAxis.labels.angle = 90
	bc.categoryAxis.labels.fontSize = 6
	bc.barLabels.fontName = "Helvetica"
	bc.barLabels.fontSize = 6
	#bc.barLabels.fillColor = black
	bc.barLabelFormat = '%d'
	bc.barLabels.nudge = 7
	bc.barLabels.angle = 90
	#bc.title = "kasun"
	#bc.categoryAxis.categoryNames = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D']
	#bc.categoryAxis.categoryNames = [(gnName[0])]
	bc.categoryAxis.categoryNames = []
	for ii in xrange(len(gnNamee)):
		bc.categoryAxis.categoryNames.append(str(gnNamee[ii]))	
	
	#bc.bars[0].fillColor = colors.blue
	#bc.bars[1].fillColor = color02
	#pdf_chart_colors = [
	#HexColor("#0000e5"),
    	#HexColor("#1f1feb"),
    	#HexColor("#5757f0"),
    	#HexColor("#8f8ff5"),
    	#HexColor("#c7c7fa"),
    	#HexColor("#f5c2c2"),
    	#HexColor("#eb8585"),
    	#HexColor("#e04747"),
    	#HexColor("#d60a0a"),
    	#HexColor("#cc0000"),
    	#HexColor("#ff0000"),
    	#]
	#n = len(bc.data)  
        #self.setItems(n,bc.bars,'fillColor',pdf_chart_colors)
	#bc.bars[0].fillColor = colors.yellow
	#bc.bars[1].fillColor = colors.green
	#bc.bars[2].fillColor = colors.blue
	#bc.bars[3].fillColor = colors.red
  
	drawing.add(bc)
	the_canvas = canvas.Canvas("Roads_inundated_Summary.pdf")
	renderPDF.draw(drawing, the_canvas, 0, 350)
	font_variants = ("DejaVuSans","DejaVuSansMono-Bold","DejaVuSans-Bold")
	folder = '/usr/share/fonts/truetype/dejavu/'
	for variant in font_variants:
    		pdfmetrics.registerFont(TTFont(variant, os.path.join(folder, variant+'.ttf')))
	the_canvas.setFont('DejaVuSans-Bold', 20)
	the_canvas.drawString(40,800,"Summary of Roads Inundated")
	the_canvas.setFont('DejaVuSans', 10)
	the_canvas.drawString(30,785,"Length (~m)")
	detailz1 = "Majority of roads inundated due to " + str(floodLyrForRpt) + ", located in, " + highest + " GND of "
	detailz2 =  str(dsS) + " DS, " + str(diS) + ", " + str(prV) + " Province - Which is " + str(disMax) + " meters"
	the_canvas.setFont('DejaVuSansMono-Bold', 10) 
	the_canvas.drawString(40,275,str(detailz1))
	the_canvas.drawString(40,255,str(detailz2))
	the_canvas.showPage()
	the_canvas.save()
	#show
	webbrowser.open('Roads_inundated_Summary.pdf')

	# pie chart
	#d = Drawing(200, 100)
	#pc = Pie()
	#pc.x = 65
	#pc.y = 15
	#pc.width = 200
	#pc.height = 200
	#pc.data = [10,20,30,40,50,60]
	# pc.data = [gnCnt]
	# pc.labels = [gnName]
	#pc.labels = ['a','b','c','d','e','f']
	# pc.slices.strokeWidth=0.5
	# pc.slices[3].popout = 10
	# pc.slices[3].strokeWidth = 2
	# pc.slices[3].strokeDashArray = [2,2]
	# pc.slices[3].labelRadius = 1.75
	# pc.slices[3].fontColor = colors.red
	#d.add(pc)
	#renderPDF.draw(d, the_canvas, 0, 0)
	#the_canvas.showPage()
	#the_canvas.save()
	

    def setItems(self, n, obj, attr, values):
    	m = len(values)
	i = m // n
	for j in xrange(n):
    		setattr(obj[j],attr,values[j*i % m])



    def clearBRoadsCat(self):
	self.dlg.ui.txtBlockedRdsCat.clear()
	self.dlg.ui.lblProvince.setVisible(False)
	self.dlg.ui.cmbProvince.setVisible(False)
	self.dlg.ui.btnProvinceOk.setVisible(False)
	self.dlg.ui.lblDistrict.setVisible(False)
	self.dlg.ui.cmbDistrict.setVisible(False)
	self.dlg.ui.btnDistOk.setVisible(False)
	self.dlg.ui.lblDS.setVisible(False)
	self.dlg.ui.cmbDS.setVisible(False)
	self.dlg.ui.btnDSOk.setVisible(False)
	self.dlg.ui.lblGND.setVisible(False)
	self.dlg.ui.cmbGND.setVisible(False)
	self.dlg.ui.btnGNDOk.setVisible(False)
	self.dlg.ui.lblDSDesc.setVisible(False)
	self.dlg.ui.lblGNDDesc.setVisible(False)
	self.dlg.ui.lblSortByR.setVisible(False)
	self.dlg.ui.cmbSortByAdmin.setVisible(False)
	self.dlg.ui.rdAscSort.setVisible(False)
	self.dlg.ui.lblAsc.setVisible(False)
	self.dlg.ui.rdDescSort.setVisible(False)
	self.dlg.ui.lblDesc.setVisible(False)
	#radio buttons
	self.groupMain.setExclusive(False)	
	self.dlg.ui.rdAllBlocked.setChecked(False)
	self.dlg.ui.rdCatBlocked.setChecked(False)
	self.groupMain.setExclusive(True)
	self.groupSub.setExclusive(False)
	self.dlg.ui.rdAscSort.setChecked(False)
	self.dlg.ui.rdDescSort.setChecked(False)
	self.groupSub.setExclusive(True)		





    ##********************************************************************dishum hosp********************************************#

#**************************************************** Generate map steps process_Dish********************************************#
    def stepsUpHos(self):
	stepz = self.genMapStepsHos() 
	#self.dlg.ui.txtStepsN.setText(stepz[0])
	#global n
	#n = 1
	global nowHos
	nowHos = nowHos - 1
	global nHos
	nHos = nHos - 1
	if nowHos < 1:
		self.dlg.ui.txtStepsN.setText(stepz[0])
		nHos = 1
	if nowHos == 1:
		self.dlg.ui.txtStepsN.setText(stepz[0])
	if nowHos == 2:
		self.dlg.ui.txtStepsN.setText(stepz[1])
	if nowHos == 3:
		self.dlg.ui.txtStepsN.setText(stepz[2])
	if nowHos == 4:
		self.dlg.ui.txtStepsN.setText(stepz[3])
	if nowHos == 5:
		self.dlg.ui.txtStepsN.setText(stepz[4])
	if nowHos == 6:
		self.dlg.ui.txtStepsN.setText(stepz[5])

	
		

    def stepsDownHos(self):
	stepz = self.genMapStepsHos()
	global nowHos
	global nHos
	nHos = nHos + 1
	
	if nHos == 1:
		self.dlg.ui.txtStepsN.setText(stepz[0])
		nowHos = 1
	if nHos == 2:
		self.dlg.ui.txtStepsN.setText(stepz[1])
		nowHos = 2
	if nHos == 3:
		self.dlg.ui.txtStepsN.setText(stepz[2])
		nowHos = 3
	if nHos == 4:
		self.dlg.ui.txtStepsN.setText(stepz[3])
		nowHos = 4
	if nHos == 5:
		self.dlg.ui.txtStepsN.setText(stepz[4])
		nowHos = 5
	if nHos == 6:
		self.dlg.ui.txtStepsN.setText(stepz[5])
		nowHos = 6
	if nHos == 7:
		self.dlg.ui.txtStepsN.setText(stepz[6])
		nowHos = 7
	if nHos > 7:
		self.dlg.ui.txtStepsN.setText(stepz[6])
		nowHos = 7

	

    def genMapStepsHos(self):
	stepsN = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>' 
	one = "<b>Step 1</b> : Load the " + clBl + "flood-hazard layer " + clBls + "and " + clBl + "map of hospital layer " + clBls
	two = "<b>Step 2</b> : Check whether a file with " + clR + ".keywords " + clRs + "extension, is available in each layer bundle "
	three = "<b>Step 3</b> : If (.keywords files) available, press on " + clBl + "Generate map for process " + clBls + "button to generate a " + clBl + "flood-safe " + clBls + "layer "
	four = "<b>Step 4</b> : If (.keywords files) " + clR + "not " + clRs + "available, select the " + clBl + "flood-hazard layer " + clBls + "and " + clBl + "map of hopital layer " + clBls + "from the drop downs and provide a name for the output shapefile "
	five = "<b>Step 5</b> : " + clR + "(If followed step 4) " + clRs + "press on " + clBl + "Generate map " + clBls + "button to generate a " + clBl + "flood-safe " + clBls + "layer "
	six = "<b>Step 6</b> : The generated " + clBl + "flood-safe " + clBls + "layer will be automatically loaded to the TOC and will be saved in your " + clBl + "/home " + clBls + "directory "
	seven = clR + "<b><h3>now you can start</h3></b> " + clRs  	

	self.dlg.ui.txtStepsN.clear()	
	stepsN.append(one)
	stepsN.append(two)
	stepsN.append(three)
	stepsN.append(four)
	stepsN.append(five)
	stepsN.append(six)
	stepsN.append(seven)
	
	#return one, two, three, four, five, six, seven
	return stepsN

#******************************************************Generate map steps process_Dish End************************************************#

###**********************************Keywords Dish**************************************************************************##
    def generateMapHos(self):
	self.keywords_from_layersHos()
 
    layer_HospitalsNonAffected= ''
    
    def generateMapManuallyHos(self):
	global bdPathN
#	allLayersLoaded = self.canvas.layers()
# 	for SelLayer in allLayersLoaded:	
#		self.dlg.ui.cboRoadLayer.addItem(SelLayer.name())
#                self.dlg.ui.cboFloodLayer.addItem(SelLayer.name())	
	BuildingLayer = self.dlg.ui.cmbSelectBuildingLayerN.currentText()	
	global floodLayerN
	floodLayerN = self.dlg.ui.cmbSelectFloodLayerN.currentText()
	outputFileN = self.dlg.ui.txtOutputShapefileN.text()
	allLayersList = self.canvas.layers()
 	for getLayer in allLayersList:
		if str(getLayer.name()) == str(BuildingLayer):
			bdPathN = str(getLayer.source())
		elif str(getLayer.name()) == str(floodLayerN):
			fdPathN = str(getLayer.source())
	outputN = os.path.splitext(bdPathN)[0]
	outputN += '_'+outputFileN+'.shp'
	##processing.runandload("qgis:difference", rdPath, fdPath, output)
	processing.runandload("qgis:difference", bdPathN, fdPathN, outputN)
	wbN = QgsVectorLayer(outputN, outputFileN, 'ogr')
       
	if wbN.isValid():
           
		QgsMapLayerRegistry.instance().addMapLayer(wbN)
                global layer_HospitalsNonAffected
                layer_HospitalsNonAffected= wbN
             
	else:
		print "No layer found"

	#active new layer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		if str(getLayerNew.name()) == str(outputFileN):
			legend.setLayerVisible(getLayerNew, True)
		elif str(getLayerNew.name()) == str(floodLayerN):
			legend.setLayerVisible(getLayerNew, True)
		else: 
			legend.setLayerVisible(getLayerNew, False)

	
    def clearGenMapFieldsHos(self):
	self.dlg.ui.txtOutputShapefileN.clear()
	self.dlg.ui.cmbSelectBuildingLayerN.clear()
        self.dlg.ui.cmbSelectFloodLayerN.clear()

	allLayersInN = self.canvas.layers()
 	for LayerNow in allLayersInN:	
		self.dlg.ui.cmbSelectBuildingLayerN.addItem(LayerNow.name())
                self.dlg.ui.cmbSelectFloodLayerN.addItem(LayerNow.name())
	colRd = '<font color="red">'
	colRds = '</font>'
	self.dlg.ui.txtStepsN.clear()
	self.dlg.ui.txtStepsN.setText(colRd + "<b>Please follow these steps</b>" + colRds + '\n' + "<b>(Press on down arrow to start)</b>")
	global nHos
	nHos = 0
	global nowHos
	nowHos = 2



    def keywords_from_layersHos(self):
	allLayersN = self.canvas.layers()
 	for oneLayer in allLayersN:	
		self.layer = oneLayer
		self.load_state_from_keywordsHos()
	global layer_path_hazN
	global layer_path_rdN
	#print layer_path_haz
	#print layer_path_rd
        #print layer_path_haz
	result_file_pathN = os.path.splitext(layer_path_rdN)[0]
        result_file_pathN += '_flood_affect.shp'
	##processing.runandload("qgis:difference", layer_path_rd, layer_path_haz, result_file_path)
	processing.runandload("qgis:difference", layer_path_rdN, layer_path_hazN, result_file_pathN)
	wbN = QgsVectorLayer(result_file_pathN, 'Hos_safe', 'ogr')
	if wbN.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wbN)
	else:
		print "No layer found"

	#active New Layer
	#global floodLayer
	#print floodLayer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
	outFileN = 'Hos_safe'
 	for getLayerNew in allLayersListNew:
		if str(getLayerNew.name()) == str(outFileN):
			legend.setLayerVisible(getLayerNew, True)
		elif str(getLayerNew.source()) == str(layer_path_hazN):
			legend.setLayerVisible(getLayerNew, True)
		else: 
			legend.setLayerVisible(getLayerNew, False)
	


	global source

#keywords files added

    def set_layerN(self):
        """Set the layer associated with the keyword editor.

        :param layer: Layer whose keywords should be edited.
        :type layer: QgsMapLayer
        """
        #self.layer = layer
	self.layer = self.canvas.currentLayer()
        self.load_state_from_keywordsHos()

    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnRemove_clicked(self):
        """Automatic slot executed when the pbnRemove button is pressed.

        Any selected items in the keywords list will be removed.
        """
        for item in self.lstKeywords.selectedItems():
            self.lstKeywords.takeItem(self.lstKeywords.row(item))
        self.leKey.setText('')
        self.leValue.setText('')
        self.update_controls_from_listN()

    def load_state_from_keywordsHos(self):
        """Set the ui state to match the keywords of the active layer.

        In case the layer has no keywords or any problem occurs reading them,
        start with a blank slate so that subcategory gets populated nicely &
        we will assume exposure to start with.

        Also if only title is set we use similar logic (title is added by
        default in dock and other defaults need to be explicitly added
        when opening this dialog). See #751

        """
        keywords = {'category': 'exposure'}

        try:
            # now read the layer with sub layer if needed
            keywords = self.keyword_io.read_keywords(self.layer)
        except (InvalidParameterError,
                HashNotFoundError):
                #NoKeywordsFoundError):
            pass

        layer_name = self.layer.name()
        #if 'title' not in keywords:
       # self.dlg.ui.txtTitleN.setText(self.layer.name())
	#print self.layer.name()
        #self.dlg.ui.lblLayerNameN.setText('Keywords for %s' % self.layer.name())

#        if 'source' in keywords:
#	    #print str(keywords['source'])
#            self.dlg.ui.txtSourceN.setText(str(keywords['source']))
#        else:
#	    #print "come"
#            self.dlg.ui.txtSourceN.setText('')

        # if we have a category key, unpack it first
        # so radio button etc get set
        if 'category' in keywords:
            self.set_category(keywords['category'])
            keywords.pop('category')
        else:
            # assume exposure to match ui. See issue #751
            self.add_list_entry('category', 'exposure')

        for key in keywords.iterkeys():
            self.add_list_entry(key, str(keywords[key]))

	if 'subcategory' in keywords:
            self.set_category(keywords['subcategory'])
	    #self.dlg.ui.txtSubcategoryN.setText(keywords['subcategory'])
	
	if str(keywords['subcategory']) == 'flood':
	    #print "come1"
	    global layer_path_hazN
	    layer_path_hazN = str(self.layer.source())
	    #print layer_path_hazN

	elif str(keywords['subcategory']) == 'structure':
            #print "come2"
	    global layer_path_rdN
	    layer_path_rdN = str(self.layer.source())
            #print layer_path_rd	

	#print layer_path_hazN
	#print layer_path_rdN
        # now make the rest of the safe_qgis reflect the list entries
        self.update_controls_from_listN()

    def update_controls_from_listN(self):
        """Set the ui state to match the keywords of the active layer."""
        #subcategory = self.get_value_for_key('subcategory')
        #units = self.get_value_for_key('unit')
        #data_type = self.get_value_for_key('datatype')
        #title = self.get_value_for_key('title')
        #if title is not None:
        #self.dlg.ui.leTitle.setText(title)
        if self.layer is not None:
            layer_name = self.layer.name()
	   # self.dlg.ui.txtTitleN.setText(self.layer.name())
            #self.dlg.ui.lblLayerNameN.setText('Keywords for %s' % layer_name)
        else:
            #self.dlg.ui.lblLayerNameN.setText('')

        #if not is_polygon_layer(self.layer):
            #self.radPostprocessing.setEnabled(False)

        # adapt gui if we are in postprocessing category
            self.toggle_postprocessing_widgets()

        #if self.dlg.ui.radExposure.isChecked():
        #    if subcategory is not None and data_type is not None:
        #        self.set_subcategory_list(
        #            self.standard_exposure_list,
        #            subcategory + ' [' + data_type + ']')
        #    elif subcategory is not None:
        #        self.set_subcategory_list(
        #            self.standard_exposure_list, subcategory)
        #    else:
        #        self.set_subcategory_list(
        #            self.standard_exposure_list,
        #            'Not Set')
        #elif self.dlg.ui.radHazard.isChecked():
            #if subcategory is not None and units is not None:
                #self.set_subcategory_list(
                    #self.standard_hazard_list,
                    #subcategory + ' [' + units + ']')
            #elif subcategory is not None:
                #self.set_subcategory_list(
                    #self.standard_hazard_list,
                    #subcategory)
            #else:
                #self.set_subcategory_list(
                    #self.standard_hazard_list,
                    #'Not Set')

        self.resize_dialogN()

    def resize_dialogN(self):
        """Resize the dialog to fit its contents."""
        # noinspection PyArgumentList
        QtCore.QCoreApplication.processEvents()

    def refresh(self):
	self.set_layerN()
#################********************************************Functions_Dish****************************************#########################
### colour the places where hospitals are situated
    def selectNonAffectedHos(self):

	global countHos
    	countHos = 0
    	self.cLayer = self.canvas.currentLayer()
	
    	global mHos
    	mHos = []
	i = 0
        #self.cLayer = self.canvas.currentLayer()   
        layer = self.iface.activeLayer()
       # if (state==Qt.Checked):
        for f in layer.getFeatures():
			#g = QgsGeometry()						
			type = f['type']
			geom = f.geometry()
			if type == 'hospital':
				fid=f.id()
				#self.cLayer.select(fid)
				point = geom.asPoint()
				print point
				#feature.color
				m1 = "locc " + str(i)
		       		m1 = QgsVertexMarker(self.canvas)
				#x=float(str(point.x()))
				#y=float(str(point.y()))
		       		m1.setCenter(point)
		       		m1.setColor(QColor(0,255,0))
		       		m1.setIconSize(6)
                       		m1.setIconType(QgsVertexMarker.ICON_BOX)
# ICON_CROSS, ICON_X
                       		m1.setPenWidth(5)
                         	countHos = countHos + 1
				i = i + 1
				mHos.append(m1)

                        

       
    def generateReportHos(self):
        
	style = getSampleStyleSheet()	
	pdf = SimpleDocTemplate("Non-affected Hospital Details.pdf")
	storyN = []
	storyDoc = []
	detailsN = []
	detailsDoc = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h2>'
	
	
	detailsN.append( h2 + clR + "<b>Non affected Hospitals - FLOOgin Report </b>" + clRs + h2s )
	global HospReport
	global DocReport

	title = clBl + "Details of people in affected Hospitals in the Area " + clBls 
	detailsN.append(str(title))
	
	#print 'x'
	t = Table(HospReport)
	
	#d = Table(DocReport)
	print 'y'
	a = 0
	coun = 1
	while a < coun:
		text = str(detailsN[a])
		if a == 0:
			storyN.append(Image("logo.png", 2*inch, 1*inch))
		if a == 1 :
			para = Paragraph(text, style['Heading2'])
		else:
			para = Paragraph(text, style["Normal"])
		storyN.append(para)
		storyN.append(Spacer(inch * .2, inch * .2))
		a = a + 1
		if a == 1:
			storyN.append( t )
		
	#detailsDoc.append(h2 + clR + "<b>Number of Registered Doctors - FLOOgin Report </b>" + clRs + h2s)

	titleDoc = clBl + "Number of Regitered Doctors " + clBls 
	detailsDoc.append(str(titleDoc))
	tDoc = Table(DocReport) 
	aDoc = 0
	counDoc = 1
	while aDoc < counDoc:
		textDoc = str(detailsDoc[aDoc])
		#if aDoc == 0:
		#	storyN.append(Image("logo.png", 2*inch, 1*inch))
		if aDoc == 0 :
			para = Paragraph(text, style['Heading2'])
		else:
			para = Paragraph(text, style["Normal"])
		#storyN.append(para)
		storyN.append(Spacer(inch * .2, inch * .2))
		aDoc = aDoc + 1
		if aDoc == 1:
			storyN.append( tDoc )		

	pdf.build(storyN)
	
#****new_d

    def generateReportHosSearch(self):
        
	style = getSampleStyleSheet()	
	pdf = SimpleDocTemplate("Non-affected Hospital details by Type.pdf")
	storyrep = []
	storysearchrep = []
	detailsSearchRep= []
	#detailsSearchRep = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h2>'
	
	
	detailsSearchRep.append( h2 + clR + "<b>Non affected Hospitals By type - FLOOgin Report </b>" + clRs + h2s )
	#global HospReport
	#global DocReport
	global searchRep

	title = clBl + "Details of people in affected Hospitals in the Area " + clBls 
	detailsSearchRep.append(str(title))
	
	#print 'x'
	t = Table(searchRep)
	
	#d = Table(DocReport)
	print 'y'
	a = 0
	coun = 1
	while a < coun:
		text = str(detailsSearchRep[a])
		if a == 0:
			storyrep.append(Image("logo.png", 2*inch, 1*inch))
		if a == 1 :
			para = Paragraph(text, style['Heading2'])
		else:
			para = Paragraph(text, style["Normal"])
		storyrep.append(para)
		storyrep.append(Spacer(inch * .2, inch * .2))
		a = a + 1
		if a == 1:
			storyrep.append( t )
	
	pdf.build(storyrep)
		

    def generateReportOtherMed(self):
        
	style = getSampleStyleSheet()	
	pdf = SimpleDocTemplate("Non-affected Other places for Medicinal assistance .pdf")
	storyOtherrep = []
	storysearchrep = []
	detailsSearchRep= []
	#detailsSearchRep = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h2>'
	
	
	detailsSearchRep.append( h2 + clR + "<b>Non affected Pharmacies & Clinics in the area  - FLOOgin Report </b>" + clRs + h2s )
	#global HospReport
	#global DocReport
	#global searchRep
	global OtherMedNeedsReport

#Pharmacies
	title = clBl + "Details of people in affected Hospitals in the Area " + clBls 
	detailsSearchRep.append(str(title))
	
	#print 'x'
	t = Table(OtherMedNeedsReport)
	
	#d = Table(DocReport)
	print 'y'
	a = 0
	coun = 1
	while a < coun:
		text = str(detailsSearchRep[a])
		if a == 0:
			storyOtherrep.append(Image("logo.png", 2*inch, 1*inch))
		if a == 1 :
			para = Paragraph(text, style['Heading2'])
		else:
			para = Paragraph(text, style["Normal"])
		storyOtherrep.append(para)
		storyOtherrep.append(Spacer(inch * .2, inch * .2))
		a = a + 1
		if a == 1:
			storyOtherrep.append( t )

#Clinics
	title = clBl + "Details of people in affected Hospitals in the Area " + clBls 
	detailsSearchRep.append(str(title))
	
	#print 'x'
	t = Table(OtherMedNeedsReport2)
	
	#d = Table(DocReport)
	print 'y'
	a = 0
	coun = 1
	while a < coun:
		text = str(detailsSearchRep[a])
		#if a == 0:
		#	storyOtherrep.append(Image("logo.png", 2*inch, 1*inch))
		if a == 0 :
			para = Paragraph(text, style['Heading2'])
		else:
			para = Paragraph(text, style["Normal"])
		storyOtherrep.append(para)
		storyOtherrep.append(Spacer(inch * .2, inch * .2))
		a = a + 1
		if a == 1:
			storyOtherrep.append( t )
	
	pdf.build(storyOtherrep)

    def generateReportHosGN(self):
        
	style = getSampleStyleSheet()	
	pdf = SimpleDocTemplate("Hospitals with GN and DS areas .pdf")
	storyGN = []
	storGNyrep = []
	detailsSearchGN= []
	#detailsSearchRep = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h2>'
	
	
	storGNyrep.append( h2 + clR + "<b>Hospitals and its GN areas  - FLOOgin Report </b>" + clRs + h2s )
	
	global GNreport

#Pharmacies
	title = clBl + "Details of people in affected Hospitals in the Area " + clBls 
	GNreport.append(str(title))
	
	#print 'x'
	t = Table(GNreport)
	
	#d = Table(DocReport)
	print 'y'
	a = 0
	coun = 1
	while a < coun:
		text = str(storGNyrep[a])
		if a == 0:
			storyGN.append(Image("logo.png", 2*inch, 1*inch))
		if a == 1 :
			para = Paragraph(text, style['Heading2'])
		else:
			para = Paragraph(text, style["Normal"])
		storyGN.append(para)
		storyGN.append(Spacer(inch * .2, inch * .2))
		a = a + 1
		if a == 1:
			storyGN.append( t )

	pdf.build(storyGN)		
#*******************************************************************************************************************************#
    def getAllHopitalsNonAffected(self):
         # if (state==Qt.Checked):
            count = 0
            for feature in self.cLayer.getFeatures():
			#g = QgsGeometry()
			buildType = self.getfieldHosType(self.cLayer) 						
			Type = feature[buildType]
			#geom = feature.geometry()
			if Type == 'hospital': #or Type == 'pharmacy' :
				fid=feature.id()
                        count = count +1
                        
            return count
            
  
    def methodCall(self, state):
        if(state==Qt.Checked):
            global NonHosCount
            dd = self.getAllHopitalsNonAffected()
            NonHosCount = dd
            self.dlg.ui.lbl_noOfHospitals.setText(str(dd))
	    self.selectNonAffectedHosTabView(state)
        
    def getPharmacyTabview(self, state):
	global countHos1
    	countHos1 = 0
    	#self.cLayer = self.canvas.currentLayer()

	k = 0
	global OtherMedNeedsReport2
	OtherMedNeedsReport2 = []
        self.cLayer = self.canvas.currentLayer()  
	tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th></th><th width="160" align="left">Type</th><th></th><th width="250" align="left">Address</th><th></th><th width="250" align="left">Telephone</th><th></th></tr>'
	OtherMedNeedsReport2.append( ['NAME', 'TYPE', 'ADDRESS','Telephone'] )
	#print 22
	self.dlg.ui.txtPharmacy.setText(tb)
	#self.dlg.setdetailfill(self.iface.showAttributeTable(self.cLayer))
        #index = self.dlg.ui.layerCombo.currentIndex()
        if (state==Qt.Checked):
            for feature in self.cLayer.getFeatures():
			#g = QgsGeometry()
			buildType = self.getfieldHosType(self.cLayer) 						
			Type = feature[buildType]
			geom = feature.geometry()
			if Type == 'pharmacy': #or Type == 'pharmacy' :
				fid=feature.id()
                      		point = geom.asPoint()
				print point
				#feature.color
				#global mHosLoc
				mHosLocc = "locc " + str(k)
		       		mHosLocc = QgsVertexMarker(self.canvas)
	   			#x=float(str(point.x()))
				#y=float(str(point.y()))
		       		mHosLocc.setCenter(point)
		       		mHosLocc.setColor(QColor(255,128,0))
		       		mHosLocc.setIconSize(6)
                       		mHosLocc.setIconType(QgsVertexMarker.ICON_BOX)
# ICON_CROSS, ICON_X
                       		mHosLocc.setPenWidth(5)

				countHos1 = countHos1 + 1
				k = k + 1
				mHos1.append(mHosLocc)

                      		name = self.getFieldHosName(self.cLayer)
				add = self.getfieldHosAddress(self.cLayer)
				phone = self.getFieldPhone(self.cLayer)
				#docs = self.getFieldNumberofDoctors(self.cLayer)

				BType = feature[buildType]
				BName = feature[name]
				BAddress = feature[add]
				Bphone = feature[phone]
				#BCapacity = feature[docs]

				a=str(BType)
				b=str(BName)
				c=str(BAddress)
				d=str(Bphone)
				#c=str(BCapacity)
				self.dlg.ui.txtPharmacy.append('<tr><td width="250">' + b + '</td><td></td><td width="160">' + a + '</td><td></td><td width="250">' + c + '</td><td></td><td width="250">' + d + '</td><td></td></tr>')		
	#self.iface.showAttributeTable(self.cLayer)
				OtherMedNeedsReport2.append( [str(BName), str(BType), str(BAddress), str(Bphone)] )
			else:
				#print "come"
				caps = self.cLayer.dataProvider().capabilities()
    

    def getClinicDetailsTabview(self, state):
 	 global countHos2
    	 countHos2 = 0
    	 #self.cLayer = self.canvas.currentLayer()

	 j = 0        
	 global OtherMedNeedsReport
	 OtherMedNeedsReport = []
         self.cLayer = self.canvas.currentLayer()  
         tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th></th><th width="160" align="left">Type</th><th></th><th width="250" align="left">Address</th><th></th><th width="250" align="left">Phone</th><th></th></tr>'
	 OtherMedNeedsReport.append( ['NAME', 'TYPE', 'ADDRESS','Telephone'] )
	#print 22
         self.dlg.ui.txtClinics.setText(tb)
	#self.dlg.setdetailfill(self.iface.showAttributeTable(self.cLayer))
        #index = self.dlg.ui.layerCombo.currentIndex()
         if (state==Qt.Checked):
            for feature in self.cLayer.getFeatures():
			#g = QgsGeometry()
			buildType = self.getfieldHosType(self.cLayer) 						
			Type = feature[buildType]
			geom = feature.geometry()
			if Type == 'clinic': #or Type == 'pharmacy' :
				fid=feature.id()
                      		point = geom.asPoint()
				print point
				#feature.color

				global mHosLoc
				mHosLoccc = "locc " + str(j)
				
		       		mHosLoccc = QgsVertexMarker(self.canvas)
	   			#x=float(str(point.x()))
				#y=float(str(point.y()))
		       		mHosLoccc.setCenter(point)
		       		mHosLoccc.setColor(QColor(255,255,0))
		       		mHosLoccc.setIconSize(6)
                       		mHosLoccc.setIconType(QgsVertexMarker.ICON_BOX)
# ICON_CROSS, ICON_X
                       		mHosLoccc.setPenWidth(5)
				countHos2 = countHos2 + 1
				j = j + 1
				mHos2.append(mHosLoccc)

                      		name = self.getFieldHosName(self.cLayer)
				#name = self.getFieldHosName(self.cLayer)
				add = self.getfieldHosAddress(self.cLayer)
				phone = self.getFieldPhone(self.cLayer)
				#docs = self.getFieldNumberofDoctors(self.cLayer)
				BType = feature[buildType]
				BName = feature[name]
				BAddress=feature[add] 
				Bphone=feature[phone]
				#BCapacity = feature[docs]
				a=str(BType)
				b=str(BName)
				c=str(BAddress)
				d=str(Bphone)
				#c=str(BCapacity)
				self.dlg.ui.txtClinics.append('<tr><td width="250">' + b + '</td><td></td><td width="160">' + a + '</td><td></td><td width="250">' + c + '</td><td width="250">' + d + '</td><td></td></tr>')		
	#self.iface.showAttributeTable(self.cLayer)
				OtherMedNeedsReport.append( [str(BName), str(BType),  str(BAddress), str(Bphone)] )
			else:
				#print "come"
				caps = self.cLayer.dataProvider().capabilities()
    
    def getDocsTabview(self, state):
	global countHos3
    	countHos3 = 0
    	#self.cLayer = self.canvas.currentLayer()
    	#global mHos3
    	#mHos3 = []
	#i = 0
	global DocReport
	DocReport = []
        self.cLayer = self.canvas.currentLayer()  
	tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th></th><th width="160" align="left">Type</th><th></th><th width="100" align="left">Registerd Doctors</th></tr>'
	#print 22
	DocReport.append( ['NAME', 'TYPE', 'Registered Doctors'] )
	self.dlg.ui.txtBDoctorsN.setText(tb)
	#self.dlg.setdetailfill(self.iface.showAttributeTable(self.cLayer))
        #index = self.dlg.ui.layerCombo.currentIndex()
        if (state==Qt.Checked):
            for feature in self.cLayer.getFeatures():
			#g = QgsGeometry()
			buildType = self.getfieldHosType(self.cLayer) 						
			Type = feature[buildType]
			geom = feature.geometry()
			if Type == 'hospital': #or Type == 'pharmacy' :
				fid=feature.id()
                      		point = geom.asPoint()
				print point
				#feature.color
				#global mHosLoc
				#mHosLoc = "locc " + str(i)
		       		#mHosLoc = QgsVertexMarker(self.canvas)
	   			#x=float(str(point.x()))
				#y=float(str(point.y()))
		       		#mHosLoc.setCenter(point)
		       		#mHosLoc.setColor(QColor(153,0,153))
		       		#mHosLoc.setIconSize(6)
                       		#mHosLoc.setIconType(QgsVertexMarker.ICON_X)
# ICON_CROSS, ICON_X
                       		#mHosLoc.setPenWidth(5)
				countHos3 = countHos3 + 1
				#i = i + 1
				#mHos3.append(mHosLoc)

                      		name = self.getFieldHosName(self.cLayer)
				docs = self.getFieldNumberofDoctors(self.cLayer)
				BType = feature[buildType]
				BName = feature[name]
				BCapacity = feature[docs]

				a=str(BType)
				b=str(BName)
				c=str(BCapacity)
				self.dlg.ui.txtBDoctorsN.append('<tr><td width="250">' + b + '</td><td></td><td width="160">' + a + '</td><td></td><td width="100">' + c + '</td></tr>')		
	#self.iface.showAttributeTable(self.cLayer)

            			DocReport.append( [str(BName), str(BType),  str(BCapacity)] )
        else:
				#print "come"
				caps = self.cLayer.dataProvider().capabilities()
    
        
    def selectNonAffectedHosTabView(self,state): 
	global countHos
    	countHos = 0
    	self.cLayer = self.canvas.currentLayer()
	
    	global mHos
    	mHos = []
	i = 0	
	global HospReport
	HospReport = []
#	HospReport.append ( ['NAME', 'TYPE', 'NUMBER OF BEDS'] )
        self.cLayer = self.canvas.currentLayer()  
	tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th></th><th width="80" align="left">Type</th><th></th><th width="80" align="left">Beds</th><th width="80" align="left">Address</th></tr>'
	HospReport.append( ['NAME', 'TYPE', 'NUMBER OF BEDS','ADDRESS','TELEPHONE'] )
	#hoscount = 1
	self.dlg.ui.txtBNonAffectedHos.setText(tb)
	#self.dlg.setdetailfill(self.iface.showAttributeTable(self.cLayer))
        if (state==Qt.Checked):
            for feature in self.cLayer.getFeatures():
			#g = QgsGeometry()
			buildType = self.getfieldHosType(self.cLayer) 						
			Type = feature[buildType]
			geom = feature.geometry()
			if Type == 'hospital': #or Type == 'pharmacy' :
				fid=feature.id()
				#self.cLayer.select(fid)
				point = geom.asPoint()
				print point
				#feature.color
				global mHosLoc
				mHosLoc = "locc " + str(i)
		       		mHosLoc = QgsVertexMarker(self.canvas)
				#x=float(str(point.x()))
				#y=float(str(point.y()))
		       		mHosLoc.setCenter(point)
		       		mHosLoc.setColor(QColor(0,255,0))
		       		mHosLoc.setIconSize(6)
                       		mHosLoc.setIconType(QgsVertexMarker.ICON_BOX)
# ICON_CROSS, ICON_X
                       		mHosLoc.setPenWidth(5)

				countHos = countHos + 1
				i = i + 1
				mHos.append(mHosLoc)
				name = self.getFieldHosName(self.cLayer)
				beds = self.getFieldBedCapacity(self.cLayer)
				add = self.getfieldHosAddress(self.cLayer)
				phone = self.getFieldPhone(self.cLayer)

				BType = feature[buildType]
				BName = feature[name]
				BCapacity = feature[beds]
				BAddress = feature[add]
				Bphone = feature[phone]

				a=str(BType)
				b=str(BName)
				c=str(BCapacity)
				d=str(BAddress)
				e=str(Bphone)
				#global HospReport
				self.dlg.ui.txtBNonAffectedHos.append('<tr><td width="100">' + b + '</td><td></td><td width="100">' + a + '</td><td></td><td width="100">' + c + '</td><td></td><td width="100">' + d + '</td><td></td><td width="100">' + e + '</td><td></td></tr>')			
	#self.iface.showAttributeTable(self.cLayer)

				
				HospReport.append( [str(BName), str(BType),  str(BCapacity), str(BAddress), str(Bphone)] )

			#hoscount = hosCount + 1
	else:
				#print "come"
				caps = self.cLayer.dataProvider().capabilities()
#********newww**
    def GetGNDSHosTabView(self,state): 
	global countHos6
    	countHos6 = 0
    	self.cLayer = self.canvas.currentLayer()
	
    	#global mHos4
    	#mHos4 = []
	i = 0	
	global GNreport
	GNreport = []
        self.cLayer = self.canvas.currentLayer()  
	tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th></th><th width="100" align="left">Type</th><th></th><th width="100" align="left">Address</th><th width="100" align="left">DS_Division</th><th width="100" align="left">GN_Division</th></tr>'
	GNreport.append( ['NAME', 'TYPE' ,'ADDRESS' ,'DS Division', 'GN Division'] )
	#hoscount = 1
	self.dlg.ui.txtGN.setText(tb)
	#self.dlg.setdetailfill(self.iface.showAttributeTable(self.cLayer))
        if (state==Qt.Checked):
            for feature in self.cLayer.getFeatures():
			#g = QgsGeometry()
			buildType = self.getfieldHosType(self.cLayer) 						
			Type = feature[buildType]
			geom = feature.geometry()
			if Type == 'hospital' : #and Type == 'pharmacy' :
				fid=feature.id()
				#self.cLayer.select(fid)
				point = geom.asPoint()
				print point
				#feature.color
				#global mHosLoc
				#mHosLoc = "locc " + str(i)
		       		

				countHos6 = countHos6 + 1
				i = i + 1
				#mHos4.append(mHosLoc)
				name = self.getFieldHosName(self.cLayer)
				#beds = self.getFieldBedCapacity(self.cLayer)
				add = self.getfieldHosAddress(self.cLayer)
				dsdN= self.getDSdivisions(self.cLayer)
				gndN= self.getGNdivisions(self.cLayer)

				BType = feature[buildType]
				BName = feature[name]
				#BCapacity = feature[beds]
				BAddress = feature[add]
				BDSD = feature[dsdN]
				BGND = feature[gndN]

				a=str(BType)
				b=str(BName)
				#c=str(BCapacity)
				d=str(BAddress)
				e=str(BDSD)
				f=str(BGND)
				#global HospReport
				self.dlg.ui.txtGN.append('<tr><td width="100">' + b + '</td><td></td><td width="100">' + a + '</td><td></td><td width="100">' + d + '</td><td width="100">' + e + '</td><td width="100">' + f + '</td></tr>')			
	#self.iface.showAttributeTable(self.cLayer)

				
				GNreport.append( [str(BType), str(BName), str(BAddress), str(BDSD), str(BGND) ] )

			#hoscount = hosCount + 1
	else:
				#print "come"
				caps = self.cLayer.dataProvider().capabilities()

    def LableHospfeatures(self):
	#global palyr
	layerHosp = self.iface.mapCanvas().currentLayer()
	#layerLbll = self.getLayerByName(layerr) 						
	showFieldHos ='name' 
	HosName = QgsPalLayerSettings()
	HosName.readFromLayer(layerHosp)
	HosName.enabled = True #False
	HosName.fieldName = showFieldHos
	HosName.placement = QgsPalLayerSettings.AroundPoint
	HosName.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
	#palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
	HosName.writeToLayer(layerHosp)
	self.iface.mapCanvas().refresh()

############## Get column details #####	
		
    def getDSdivisions(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldDS = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "DSD_N"
			words = colHeadLower.split()
			if term in words:
				fieldDS = colHead
			d = d + 1
		if fieldDS == '':
			fieldDS = str(fields.field(12).name())
		return fieldDS

    def getGNdivisions(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldGN = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "GND_N"
			words = colHeadLower.split()
			if term in words:
				fieldGN = colHead
			d = d + 1
		if fieldGN == '':
			fieldGN = str(fields.field(13).name())
		return fieldGN
 
    def getFieldNumberofDoctors(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldDocCap = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "RDoctors"
			words = colHeadLower.split()
			if term in words:
				fieldDocCap = colHead
			d = d + 1
		if fieldDocCap == '':
			fieldDocCap = str(fields.field(5).name())
		return fieldDocCap

                
    def getfieldHosType(self, layer):
        	fields = layer.pendingFields()
        	fCount = fields.count()
        	d = 0
        	fieldHosType = ''
        	while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldHosType = colHead
			d = d + 1
                if fieldHosType == '':
			fieldHosType = str(fields.field(3).name())
		return fieldHosType

    def getFieldHosName(self, layer):
        	fields = layer.pendingFields()
        	fCount = fields.count()
        	d = 0
        	fieldHosName = ''
        	while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "name"
			words = colHeadLower.split()
			if term in words:
				fieldHosType = colHead
			d = d + 1
                if fieldHosName == '':
			fieldHosName = str(fields.field(2).name())
		return fieldHosName
#***newest
    def getFieldPhone(self, layer):
        	fields = layer.pendingFields()
        	fCount = fields.count()
        	d = 0
        	fieldPhone = ''
        	while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "Telephone"
			words = colHeadLower.split()
			if term in words:
				fieldPhone = colHead
			d = d + 1
                if fieldPhone == '':
			fieldPhone = str(fields.field(8).name())
		return fieldPhone

    def getFieldBedCapacity(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldBedCap = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "Beds"
			words = colHeadLower.split()
			if term in words:
				fieldBedCap = colHead
			d = d + 1
		if fieldBedCap == '':
			fieldBedCap = str(fields.field(4).name())
		return fieldBedCap

#*** new
    def getFieldhosType(self, layer):
        	fields = layer.pendingFields()
        	fCount = fields.count()
        	d = 0
        	fieldhosType = ''
        	while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "hosType"
			words = colHeadLower.split()
			if term in words:
				fieldhosType = colHead
			d = d + 1
                if fieldhosType == '':
			fieldhosType = str(fields.field(6).name())
		return fieldhosType

    def getfieldHosAddress(self, layer):
        	fields = layer.pendingFields()
        	fCount = fields.count()
        	d = 0
        	fieldHosAddress = ''
        	while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "Address"
			words = colHeadLower.split()
			if term in words:
				fieldHosType = colHead
			d = d + 1
                if fieldHosAddress == '':
			fieldHosAddress = str(fields.field(7).name())
		return fieldHosAddress
                
#***** Get details in text format*****#
   
    def printData(self):   
        output_file = open('hospitals.txt', 'w')
        layer = self.iface.activeLayer()
        for f in layer.getFeatures():
                  type = f['type']
                  #geom = f.geometry()
                  if type == 'hospital':
		      #Tno=str(f['Telephone'])
			
                      line = '%s, %s, %s, %s\n' % (f['name'], f['type'], f['hosType'], f['Address'])
                      unicode_line = line.encode('utf-8')
                      output_file.write(unicode_line)
           # output_file.close()

#***** clear **************************************************************
    def clearFieldsN(self):
	self.dlg.ui.lbl_noOfHospitals.clear()
	self.dlg.ui.txtBNonAffectedHos.clear()
       
	self.dlg.ui.chkNonAffected.setChecked(False)
	self.dlg.ui.txtBDoctorsN.clear()
        self.dlg.ui.txtPharmacy.clear()
        self.dlg.ui.txtClinics.clear()


    def clearGenMapFieldsHos_one(self):
	self.dlg.ui.txtOutputShapefileN.clear()
	self.dlg.ui.cmbSelectBuildingLayerN.clear()
	#self.dlg.ui.cmbSelectBuildingLayerN.clear()
        self.dlg.ui.cmbSelectFloodLayerN.clear()

	allLayersInN = self.canvas.layers()
 	for LayerNow in allLayersInN:	
		self.dlg.ui.cmbSelectBuildingLayerN.addItem(LayerNow.name())
                self.dlg.ui.cmbSelectFloodLayerN.addItem(LayerNow.name())
	colRd = '<font color="red">'
	colRds = '</font>'
	self.dlg.ui.txtStepsN.clear()
	self.dlg.ui.txtStepsN.setText(colRd + "<b>Please follow these steps</b>" + colRds + '\n' + "<b>(Press on down arrow to start)</b>")
	global nHos
	nHos = 0
	global nowHos
	nowHos = 2

    def clearGenMapFieldsHos_two(self):
	self.dlg.ui.chkNonAffected.setChecked(False)
	self.dlg.ui.lbl_noOfHospitals.clear()
        self.dlg.ui.txtBNonAffectedHos.clear()
	self.dlg.ui.txtSearchbyHos.clear()
	
	global mHos
	#print str(len(mHos))
	i = 0
	try:
		while i< len(mHos):
			print str(mHos[i])
			self.iface.mapCanvas().scene().removeItem(mHos[i])
			#del mIDPLocAll[i]
			i = i + 1
	except:
		print "OK"
	print str(i)
	self.iface.mapCanvas().refresh()

    def clearGenMapFieldsHos_three(self):
	self.dlg.ui.chknumberofDoctors.setChecked(False)
	self.dlg.ui.chkPharmacy.setChecked(False)
	self.dlg.ui.chkboxclinics.setChecked(False)
	self.dlg.ui.txtBDoctorsN.clear()
        self.dlg.ui.txtPharmacy.clear()
	self.dlg.ui.txtClinics.clear()

	global mHos1
	#print str(len(mHos))
	k = 0
	try:
		while k< len(mHos1):
			print str(mHos1[k])
			self.iface.mapCanvas().scene().removeItem(mHos1[k])
			#del mIDPLocAll[i]
			k = k + 1
	except:
		print "OK"
	print str(k)
	self.iface.mapCanvas().refresh()

	global mHos2
	#print str(len(mHos))
	j = 0
	try:
		while j< len(mHos2):
			print str(mHos2[j])
			self.iface.mapCanvas().scene().removeItem(mHos2[j])
			#del mIDPLocAll[i]
			j = j + 1
	except:
		print "OK"
	print str(j)
	self.iface.mapCanvas().refresh()

	

    def clearGenMapFieldsHos_four(self):
	self.dlg.ui.chkGN.setChecked(False)
	self.dlg.ui.txtGN.clear()
        

	


# Save as image
    def saveAsN(self):
	self.iface.mapCanvas().saveAsImage('/home/nisansala/testData.png', None, 'PNG')
	QMessageBox.information( self.iface.mainWindow(),"Info", "Map Canvas saved successfully" )
# Help Dialog
    def HelpGenerateMapN(self):
	self.dlgHelpHos.show()
        self.dlgHelpHos.uiHelpHos.tbwHos.setCurrentIndex(0)
        self.dlgHelpHos.exec_()
    
    def HelpHospDetailsN(self):
	self.dlgHelpHos.show()
        self.dlgHelpHos.uiHelpHos.tbwHos.setCurrentIndex(1)
        self.dlgHelpHos.exec_()

#***** Search Hos/phar/Clinics by GN DS************NEW

    def refreshAdminisLyrsHos(self):
	self.dlg.ui.cmbAdminLayerGN.clear()
	allLayersLoaded = self.canvas.layers()
 	for SelLayer in allLayersLoaded:		
		self.dlg.ui.cmbAdminLayerGN.addItem(SelLayer.name())

		#global HosGN
		#HosGN = self.dlg.ui.cmbAdminLayerGN.currentIndex()

    def searchHosByGN(self):

		try:
			searchHospitals = self.dlg.ui.cmbAdminLayerGN.currentText()
			#self.dlg.ui.cmbHospitalR.clear()
			if searchHospitals != 'Select Layer': #and rH == 0:
				global HosGN
				HosGN = self.getLayerByName( searchHospitals )
				#print stopHospLayer
				#print stopHospLayer.name()
				global fieldGNHos
				fieldGNHos = self.getFieldName(HosGN)
				buildType = self.getGNdivisions(HosGN)
				self.dlg.ui.cmbSerchByGN.clear() 
				for feature in HosGN.getFeatures():
					Type = feature[buildType]
					if Type == 'hospital':					
						name = feature[fieldGNHos]
						if str(name) != 'NULL':
							self.dlg.ui.cmbSerchByGN.addItem(str(name))
			#rH = 0
		except:
			e = sys.exc_info()[0]
			print e

#***** search Hospitals according to the  Type of the hospital
    def searchHos(self):

	global countHossearch
    	countHossearch = 0
	self.cLayer = self.canvas.currentLayer()

	global mHossearch
    	mHossearch = []
	i = 0	

	global searchRep
	searchRep = []
    	#self.cLayer = self.canvas.currentLayer()
	
    	
	Hosp = self.dlg.ui.cmbSearchHos.currentIndex()

	if Hosp == 0: 
		
		self.cLayer = self.canvas.currentLayer()  
		tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th></th><th width="80" align="left">Type</th><th></th><th width="80" align="left">Beds</th><th width="80" align="left">Address</th></tr>'
		searchRep.append( ['NAME', 'TYPE', 'BEDS','ADDRESS'] )
		self.dlg.ui.txtSearchbyHos.setText(tb)
		
            	for feature in self.cLayer.getFeatures():
				
			buildType = self.getFieldhosType(self.cLayer) 						
			Type = feature[buildType]
			
			geom = feature.geometry()
			if Type == 'BH':
				
				point = geom.asPoint()
				print point

				#global mHosLocb
				#mHosLocb = "locb " + str(i)

				countHossearch = countHossearch + 1
				i = i + 1

         			#mHossearch.append(mHosLocb)
				name = self.getFieldHosName(self.cLayer)
				beds = self.getFieldBedCapacity(self.cLayer)
				add = self.getfieldHosAddress(self.cLayer)

				BType = feature[buildType]
				BName = feature[name]
				BCapacity = feature[beds]
				BAddress = feature[add]

				a=str(BType)
				b=str(BName)
				c=str(BCapacity)
				d=str(BAddress)
				#global HospReport
				self.dlg.ui.txtSearchbyHos.append('<tr><td width="100">' + b + '</td><td></td><td width="100">' + a + '</td><td></td><td width="100">' + c + '</td><td width="100">' + d + '</td></tr>')		
	
				searchRep.append( [str(BName), str(BType), str(BCapacity), str(BAddress) ] )
				
	elif Hosp == 1:
		
		self.cLayer = self.canvas.currentLayer()  
		tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th></th><th width="80" align="left">Type</th><th></th><th width="80" align="left">Beds</th><th width="80" align="left">Address</th></tr>'
		searchRep.append( ['NAME', 'TYPE', 'BEDS','ADDRESS'] )
		self.dlg.ui.txtSearchbyHos.setText(tb)
		
            	for feature in self.cLayer.getFeatures():
				
			buildType = self.getFieldhosType(self.cLayer) 						
			Type = feature[buildType]
			
			geom = feature.geometry()
			if Type == 'DGH':
				
				point = geom.asPoint()
				print point
				#global mHosLocb
				#mHosLocb = "locb " + str(i)
				countHossearch = countHossearch + 1
				i = i + 1
         			#mHossearch.append(mHosLocb)

         
				name = self.getFieldHosName(self.cLayer)
				beds = self.getFieldBedCapacity(self.cLayer)
				add = self.getfieldHosAddress(self.cLayer)

				BType = feature[buildType]
				BName = feature[name]
				BCapacity = feature[beds]
				BAddress = feature[add]

				a=str(BType)
				b=str(BName)
				c=str(BCapacity)
				d=str(BAddress)
				#global HospReport
				self.dlg.ui.txtSearchbyHos.append('<tr><td width="100">' + b + '</td><td></td><td width="100">' + a + '</td><td></td><td width="100">' + c + '</td><td width="100">' + d + '</td></tr>')		
				searchRep.append( [str(BName),str(BType),  str(BCapacity), str(BAddress) ] )
	
	elif Hosp == 2:
		self.cLayer = self.canvas.currentLayer()  
		tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th></th><th width="80" align="left">Type</th><th></th><th width="80" align="left">Beds</th><th width="80" align="left">Address</th></tr>'
		searchRep.append( ['NAME', 'TYPE', 'BEDS','ADDRESS'] )
		self.dlg.ui.txtSearchbyHos.setText(tb)
		
            	for feature in self.cLayer.getFeatures():
				
			buildType = self.getFieldhosType(self.cLayer) 						
			Type = feature[buildType]
			
			geom = feature.geometry()
			if Type == 'CD':
				
				point = geom.asPoint()
				print point
				#global mHosLocb
				#mHosLocb = "locb " + str(i)
				countHossearch = countHossearch + 1
				i = i + 1
         			#mHossearch.append(mHosLocb)

         
				name = self.getFieldHosName(self.cLayer)
				beds = self.getFieldBedCapacity(self.cLayer)
				add = self.getfieldHosAddress(self.cLayer)

				BType = feature[buildType]
				BName = feature[name]
				BCapacity = feature[beds]
				BAddress = feature[add]

				a=str(BType)
				b=str(BName)
				c=str(BCapacity)
				d=str(BAddress)
				#global HospReport
				self.dlg.ui.txtSearchbyHos.append('<tr><td width="100">' + b + '</td><td></td><td width="100">' + a + '</td><td></td><td width="100">' + c + '</td><td width="100">' + d + '</td></tr>')		
	
				searchRep.append( [str(BName), str(BType), str(BCapacity), str(BAddress) ] )
	elif Hosp == 3:
		self.cLayer = self.canvas.currentLayer()  
		tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th></th><th width="80" align="left">Type</th><th></th><th width="80" align="left">Beds</th><th width="80" align="left">Address</th></tr>'
		searchRep.append( ['NAME', 'TYPE', 'BEDS','ADDRESS'] )
		self.dlg.ui.txtSearchbyHos.setText(tb)
		
            	for feature in self.cLayer.getFeatures():
				
			buildType = self.getFieldhosType(self.cLayer) 						
			Type = feature[buildType]
			
			geom = feature.geometry()
			if Type == 'TH':
				
				point = geom.asPoint()
				print point
				#global mHosLocb
				#mHosLocb = "locb " + str(i)
				countHossearch = countHossearch + 1
				i = i + 1
         			#mHossearch.append(mHosLocb)

         
				name = self.getFieldHosName(self.cLayer)
				beds = self.getFieldBedCapacity(self.cLayer)
				add = self.getfieldHosAddress(self.cLayer)

				BType = feature[buildType]
				BName = feature[name]
				BCapacity = feature[beds]
				BAddress = feature[add]

				a=str(BType)
				b=str(BName)
				c=str(BCapacity)
				d=str(BAddress)
				#global HospReport
				self.dlg.ui.txtSearchbyHos.append('<tr><td width="100">' + b + '</td><td></td><td width="100">' + a + '</td><td></td><td width="100">' + c + '</td><td width="100">' + d + '</td></tr>')		
				searchRep.append( [str(BName), str(BType), str(BCapacity), str(BAddress) ] )
#**** Generate Admin layers for Hospitals(Union)

    def refreshAdminisLyrsN(self):
	self.dlg.ui.cmbAdminLayerN.clear()
	allLayersLoaded = self.canvas.layers()
 	for SelLayer in allLayersLoaded:		
		self.dlg.ui.cmbAdminLayerN.addItem(SelLayer.name())
  
		
    def generateAdminisHosMap(self):
	global bdPathN
	global unionBRdsAdLyrN
	global bRoadsUnionPathN
	adminlayerN = self.dlg.ui.cmbAdminLayerN.currentText()
	allLayersListN = self.canvas.layers()
 	for getLayerN in allLayersListN:
		if str(getLayerN.name()) == str(adminlayerN):
			adminPathN = str(getLayerN.source())

	outputN = os.path.splitext(bdPathN)[0]
	outputN += '_HosCat.shp'
	bRoadsUnionPathN = outputN
	outputFileN = 'blockedHosCat'
	processing.runalg("qgis:union", bdPathN, adminPathN, outputN)
	wb = QgsVectorLayer(outputN, outputFileN, 'ogr')
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
	else:
		print "No layer found"
	#active new layer
	legendN = self.iface.legendInterface()
	allLayersListNewN = self.canvas.layers()
 	for getLayerNewN in allLayersListNewN:
		print "done1"
		if str(getLayerNewN.name()) == str(outputFileN):
			legend.setLayerVisible(getLayerNewN, True)
	

	allLayersListNewN = self.canvas.layers()
 	for getLayerNewN in allLayersListNewN:
		print "done2"
		if str(getLayerNewN.name()) == str(outputFileN):
			HosLayerCat = self.getLayerByName( getLayerNewN.name() )
			unionBRdsAdLyrN = HosLayerCat

	#deactive new layer
	legenddN = self.iface.legendInterface()
	allLayersListNewwN = self.canvas.layers()
 	for getLayerNewwN in allLayersListNewwN:
		if str(getLayerNewwN.name()) == str(outputFileN):
			legenddN.setLayerVisible(getLayerNewwN, False)
						
	
##################################**********************************End_Functions_Dish*********************************###############################################



  

    ##**********************************************************************dil IDP****************************************************#
    def popResetIDP(self):
	self.dlg.ui.cmbSelectPopLayer.clear()
	allLayersIn = self.canvas.layers()
 	for LayerNow in allLayersIn:	
		self.dlg.ui.cmbSelectPopLayer.addItem(LayerNow.name())
	
    def generateReportIDP(self):
	global IDPReport
	global xIDP
	global yIDP
	global startNameIDP
	global rangeIDP

	style = getSampleStyleSheet()	
	pdf = SimpleDocTemplate("Non-affected IDP camps.pdf")
	story = []
	details = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h1>'
	#0
	details.append( h2 + clR + "<b>Non affected IDP camps - FLOOgin Report </b>" + clRs + h2s )
	#1
	topic1 = clBl + "Details of Non-affected IDP camps " + clBls 
	details.append(str(topic1))
	#2
	topic2 = clBl + "Find areas of availability " + clBls 
	details.append(str(topic2))
	#3
	topic3= clBl + "IDP camps in  Coordination  : X : "+ clBls + str(xIDP) + " , " + clBl + " Y : " + clBls + str(yIDP) + clBl + " within " + clBls + str(rangeIDP) + clBl +" m " + clBls 
	details.append(str(topic3))	
	#4
	topic4 = clBl + "Details of people in affected area " + clBls 
	details.append(str(topic4))
	#5
	t=Table(IDPReport)
	#6
	p=Table(fdpopForReport)
	
	a = 0
	coun = 5
	while a < coun:
		text = str(details[a])
		print text
		if a == 0:
			story.append(Image("logo.png", 2*inch, 1*inch))
			para = Paragraph(text, style['Heading2'])
			story.append(para)
			#print a
		elif a == 1 or a == 2 or a == 5:
			para = Paragraph(text, style['Heading2'])
			story.append(para)
			#print a
		#elif a == 2:
			#story.append( t )
			#print a
		#elif a == 1:
			#para = Paragraph(text, style["Normal"])
			#story.append(para) 
		#if a != 0 or a != 1 or a != 2 or a != 3 or a != 4:
		#	para = Paragraph(text, style["Normal"])
		#	story.append(para) 
		#	print a
		else:
			para = Paragraph(text, style["Normal"])
			story.append(para) 				
		#story.append(para)
		story.append(Spacer(inch * .2, inch * .2))
		a = a + 1
		if a == 2:
			story.append( t )
		if a == 5:
			story.append( p )
		
		
	pdf.build(story)
	


    def helpDialogIDPStart(self):
	# show the dialog
        self.dlgHelpIDP.show()
        # Run the dialog event loop
	self.dlgHelpIDP.uiHelpIDP.tbwIDP.setCurrentIndex(0)
        self.dlgHelpIDP.exec_()

    def helpDialogIdentifyIDP(self):
	# show the dialog
        self.dlgHelpIDP.show()
        # Run the dialog event loop
	self.dlgHelpIDP.uiHelpIDP.tbwIDP.setCurrentIndex(1)
        self.dlgHelpIDP.exec_()

    def helpDialogNearByIDP(self):
	# show the dialog
        self.dlgHelpIDP.show()
        # Run the dialog event loop
	self.dlgHelpIDP.uiHelpIDP.tbwIDP.setCurrentIndex(2)
        self.dlgHelpIDP.exec_()

    def helpDialogVictimIDP(self):
	# show the dialog
        self.dlgHelpIDP.show()
        # Run the dialog event loop
	self.dlgHelpIDP.uiHelpIDP.tbwIDP.setCurrentIndex(3)
        self.dlgHelpIDP.exec_()

    def helpDialogavailIDP(self):
	# show the dialog
        self.dlgHelpIDP.show()
        # Run the dialog event loop
	self.dlgHelpIDP.uiHelpIDP.tbwIDP.setCurrentIndex(3)
        self.dlgHelpIDP.exec_()

    def helpDialogCloseIDP(self):
	self.dlgHelpIDP.hide()


    def floodVictimsDetails(self):
	global fdpopForReport
	fdpopForReport = []	
	global fdPathIDP
	global popVictimsLayer
	global layer_path_haz
	if fdPathIDP == '':
		fdPathIDP = layer_path_haz
	popLayer = str(self.dlg.ui.cmbSelectPopLayer.currentText())
	allLayersList = self.canvas.layers()
 	for getLayer in allLayersList:
		print "y"
		if str(getLayer.name()) == str(popLayer):
			print "y"
			popPath = str(getLayer.source())

	output = os.path.splitext(popPath)[0]
	output += '_Affected.shp'
	outputFile = 'floodVictims'
	processing.runalg("qgis:intersection", popPath, fdPathIDP, output)
	#allLayersListNew = self.canvas.layers()

	wb = QgsVectorLayer(output, outputFile, 'ogr')
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
	else:
		print "No layer found"
	#active new layer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		print "x"
		if str(getLayerNew.name()) == str(outputFile):
			print "y"
			legend.setLayerVisible(getLayerNew, True)
			#popVictimsLayer = self.getLayerByName( getLayerNew.name() )
			
	allLayersListNewW = self.canvas.layers()
 	for getLayerNewW in allLayersListNewW:
		print "y"
		if str(getLayerNewW.name()) == str(outputFile):
			print "y"
			popVictimsLayer = self.getLayerByName( getLayerNewW.name() )
			print str(popVictimsLayer.name())


	try: 
		self.dlg.ui.txtFloodVictims.clear()
		b = '<b>'
		bs = '</b>'
		#colHeads = b + 'Name     Type     Class     Oneway     Bridge     Tunnel ' + bs + '\n'
		colHeads = '<table style="width:300px"><tr><th width="150" align="left">GN Division</th><th></th><th width="50" align="left">Male</th><th></th><th width="60" align="left">Female</th><th></th><th width="60" align="left">Age_U_18</th><th></th><th width="60" align="left">Age_O_18</th><th></th><th width="70" align="left">Area km^2</th><th></th><th width="60" align="left">Density</th></tr>'
		self.dlg.ui.txtFloodVictims.setText( colHeads )
		fdpopForReport.append( ['GN Division','Male', 'Female', 'Age_U_18', 'Age_O_18', 'Area km','Density'] )
 		#bRoadsfCount = 1
		maleCount = 0
		femaleCount = 0
		ageUnd18Count = 0
		ageAbv18Count = 0
		areaSum = 0.0
		cc = 0
		dsPopList = []
		for feature in popVictimsLayer.getFeatures():
			print "y"					
			gnd = feature['GND_N']
			male = feature['MALE']
			female = feature['FEMALE']		
			ageUnd18 = feature['AGE_U_18']
			ageAbv18 = feature['AGE_O_18']
			area = feature['Area_km2']
			density = feature['Density']
			dsPop = feature['DSD_N']
			dsPopList.append(dsPop)
			#values = str(name) + '\t\t\t' + str(typee) + '\t' + str(ref) + '\t' + str(oneway) + '\t' + str(bridge) + '\t' + str(tunnel) + '\n'
			values = '<tr><td width="150">' + str(gnd) + '</td><td></td><td width="50">' + str(int(male)) + '</td><td></td><td width="60">' + str(int(female)) + '</td><td></td><td width="60">' + str(int(ageUnd18)) + '</td><td></td><td width="60">' + str(int(ageAbv18)) + '</td><td></td><td width="70">' + str(area) + '</td><td></td><td width="60">' + str(density) + '</td></tr><tr></tr>'
			self.dlg.ui.txtFloodVictims.append( values )

			maleCount = maleCount + int(male)
			femaleCount = femaleCount + int(female)
			ageUnd18Count = ageUnd18Count + int(ageUnd18)
			ageAbv18Count = ageAbv18Count + int(ageAbv18)
			areaSum = areaSum + float(area)
			cc = cc + 1
			fdpopForReport.append( [str(gnd), str(int(male)), str(int(female)), str(int(ageUnd18)),  str(int(ageAbv18)), str(area),str(density)  ] )
			#bRoadsfCount = bRoadsfCount + 1
		#self.dlg.ui.txtBlockedRoads.append( '</table>' )

		totVictims = maleCount + femaleCount
		clBl = '<font color="blue">'
		clBls = '</font>'
		clR = '<font color="red">'
		clRs = '</font>' 
		self.dlg.ui.txtFloodVictims.append( clBl + '<b>Summary</b>' + clBls + '\n')
		#self.dlg.ui.txtFloodVictims.append( '\n' )
		self.dlg.ui.txtFloodVictims.append( 'Families lived in, total of ' + '<b>' + str(cc) + '</b>' + ' GN Divisions, have been affected by flood \n')
		self.dlg.ui.txtFloodVictims.append( '\n' )
		self.dlg.ui.txtFloodVictims.append( '<b>Affected area</b>\t          : ' + str(areaSum) + ' km^2\n' )
		self.dlg.ui.txtFloodVictims.append( '<b>Victims - male</b>\t         : ' + str(maleCount) + '\n' )
		self.dlg.ui.txtFloodVictims.append( '<b>Victims - female</b>\t       : ' + str(femaleCount) + '\n' )
		self.dlg.ui.txtFloodVictims.append( '<b>Victims - Age Under 18</b>\t : ' + str(ageUnd18Count) + '\n' )
		self.dlg.ui.txtFloodVictims.append( '<b>Victims - Age Above 18</b>\t : ' + str(ageAbv18Count) + '\n' )
		self.dlg.ui.txtFloodVictims.append( '<b>Victims - Total</b>\t        : ' + clR + str(totVictims) + clRs + '\n' )

		#deactive new layer
		legenddd = self.iface.legendInterface()
		allLayersListNewww = self.canvas.layers()
 		for getLayerNewww in allLayersListNewww:
			if str(getLayerNewww.name()) == str(outputFile):
				legenddd.setLayerVisible(getLayerNewww, False)

		global dsUnique 
		dsUnique = []
		dsUnique.append( dsPopList[0] )
		for typ in dsPopList:
			if not typ in dsUnique:
				dsUnique.append(typ)
		

	except:
		e = sys.exc_info()#[0]
		print e

#*****************************dil new added

    def checkIDPCapacityAvail(self):
	global popVictimsLayer
	#global dsUnique
	global IDPSafePathManu
	global IDPSafePath
	global IDPSafeUnionLayer

	if IDPSafePath == '':
		IDPSafePath = IDPSafePathManu	
			
	dsLayer = self.dlg.ui.cmbDSLayerIDP.currentText()
	allLayersList = self.canvas.layers()
 	for getLayer in allLayersList:
		if str(getLayer.name()) == str(dsLayer):
			dsPath = str(getLayer.source())

	output = os.path.splitext(IDPSafePath)[0]
	output += '_Avail.shp'
	IDPUnionPath = output
	outputFile = 'IDPSafeWithDS'
	processing.runalg("qgis:union", IDPSafePath, dsPath, output)
	wb = QgsVectorLayer(output, outputFile, 'ogr')
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
	else:
		print "No layer found"
	#active new layer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		print "done1"
		if str(getLayerNew.name()) == str(outputFile):
			legend.setLayerVisible(getLayerNew, True)
	

	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		print "done2"
		if str(getLayerNew.name()) == str(outputFile):
			IDPSafeUnionLayer = self.getLayerByName( getLayerNew.name() )

	#deactive new layer
	legendd = self.iface.legendInterface()
	allLayersListNeww = self.canvas.layers()
 	for getLayerNeww in allLayersListNeww:
		if str(getLayerNeww.name()) == str(outputFile):
			legendd.setLayerVisible(getLayerNeww, False)
	
		
					

    def showIDPAvail(self):
	global popVictimsLayer
	global IDPSafeUnionLayer
	global dsUnique
	clR = '<font color="red">'
	clRs = '</font>'
	dsSel = self.dlg.ui.cmbDSSelectIDP.currentText()
	self.dlg.ui.txtIDPSafeAvail.setText('')
	self.dlg.ui.txtIDPNearbyAvail.clear()
	totCap = 0
	for feature in IDPSafeUnionLayer.getFeatures():					
		dsd = feature['NAME_2']
		idpName = feature['name']
		cap = feature['capacity']
		IDPTy = feature['type']
		if str(dsd) != 'NULL': 
			if (str(IDPTy) == 'school' or str(IDPTy) == 'place_of_worship' or str(IDPTy) =='temple'):
				if str(dsd) == str(dsSel):
					totCap = totCap + int(cap)
	totPop = 0
	for feature in popVictimsLayer.getFeatures():
		dsPop = feature['DSD_N']
		tp = feature['TP']
		if str(dsPop) == str(dsSel):
			totPop = totPop + int(tp)
	

	detPrint1 = "Divisional Secretariat(DS) : " + str(dsSel)
	detPrint2 = "Total Population affected : " + str(totPop)
	detPrint3 = "Total Capacity Available : " + str(totCap)					
	self.dlg.ui.txtIDPSafeAvail.append( str(detPrint1) )
	self.dlg.ui.txtIDPSafeAvail.append( str(detPrint2) )
	self.dlg.ui.txtIDPSafeAvail.append( str(detPrint3) )

	if int(totPop) > int(totCap):
		detPrint4 = clR + "Available Capacity may insufficient. Please check nearby IDP Camps " + clRs 		
		self.dlg.ui.txtIDPSafeAvail.append( str(detPrint4) )

		colHeads = '<table style="width:300px"><tr><th width="150" align="left">NAME</th><th></th><th width="120" align="left">TYPE</th><th></th><th width="80" align="left">CAPACITY</th><th></th><th width="100" align="left">DS</th></tr>'
		self.dlg.ui.txtIDPNearbyAvail.setText( colHeads )
		for feature in IDPSafeUnionLayer.getFeatures():					
			dsdd = feature['NAME_2']
			IDPTyp = feature['type']
			IDPNm = feature['name']
			IDPCap = feature['capacity']
			if str(dsdd) != 'NULL': 
				if (str(IDPTyp) == 'school' or str(IDPTyp) == 'place_of_worship' or str(IDPTyp) =='temple'):
					if not dsdd in dsUnique:
						val = '<tr><td width="150">' + str(IDPNm) + '</td><td></td><td width="120">' + str(IDPTyp) + '</td><td></td><td width="80">' + str(int(IDPCap)) + '</td><td></td><td width="100">' + str(dsdd) + '</td></tr><tr></tr>'
						self.dlg.ui.txtIDPNearbyAvail.append( val )
						

    def clearIDPAvailCap(self):
	self.dlg.ui.txtIDPSafeAvail.clear()
	self.dlg.ui.txtIDPNearbyAvail.clear()		
				 

    def dsLayerIndexChanged(self):
	self.dlg.ui.cmbDSSelectIDP.clear()
	global dsUnique
	for d in dsUnique:
		self.dlg.ui.cmbDSSelectIDP.addItem(str(d))
		

    def refreshDSLayerIDP(self):
	self.dlg.ui.cmbDSLayerIDP.clear()
	allLayersLoadedd = self.canvas.layers()
 	for SelLayerr in allLayersLoadedd:	
		self.dlg.ui.cmbDSLayerIDP.addItem(SelLayerr.name())

    def refreshPopLayerIDP(self):
	self.dlg.ui.cmbSelectPopLayer.clear()
	allLayersLoadedd = self.canvas.layers()
 	for SelLayerr in allLayersLoadedd:	
		self.dlg.ui.cmbSelectPopLayer.addItem(SelLayerr.name())
	

    def ClearnonaffecIDP(self):
	self.dlg.ui.txtDetails.clear()
	layerr = self.iface.mapCanvas().currentLayer() 						
	showFieldd ='capacity' 
	palyr = QgsPalLayerSettings()
	palyr.readFromLayer(layerr)
	palyr.enabled = False
	palyr.fieldName = showFieldd
	palyr.placement = QgsPalLayerSettings.OverPoint
	palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
	#palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
	palyr.writeToLayer(layerr)
	global countIDP
	print str(countIDP)
	global mIDPLocAll
	print str(len(mIDPLocAll))
	i = 0
	try:
		while i< len(mIDPLocAll):
			print str(mIDPLocAll[i])
			self.iface.mapCanvas().scene().removeItem(mIDPLocAll[i])
			#del mIDPLocAll[i]
			i = i + 1
	except:
		print "OK"
	print str(i)
	self.iface.mapCanvas().refresh()


    def clearFloodVictims(self):
	self.dlg.ui.txtFloodVictims.clear()
	self.dlg.ui.cmbSelectPopLayer.clear()
	allLayersLoaded = self.canvas.layers()
 	for SelLayer in allLayersLoaded:	
		self.dlg.ui.cmbSelectPopLayer.addItem(SelLayer.name())
	

    def clearIDPLoc(self):
	self.dlg.ui.txtDetails.clear()	
	#self.dlg.ui.chkNonaffectIDP.setChecked(False)
	#self.dlg.ui.chkshowAll.setChecked(False)
	try:		
		global mIDPLoc
		self.canvas.scene().removeItem(mIDPLoc)
	except:
		e = sys.exc_info()#[0]
		print e

    def clearIDPNearby(self):
	global vlI
	global lyrTempLine
	global mIDPDetails
	print "comeeeeeeeeeeeeeeeeeee"
	self.dlg.ui.txtLocNameIDP.clear()
	self.dlg.ui.txtLocCodiIDP.clear()
	self.dlg.ui.txtNearIDPDetails.clear()
	try:		
		global rbIDPAll
		i = 0
		while i < len(rbIDPAll):
			print "x"
			self.iface.mapCanvas().scene().removeItem(rbIDPAll[i])
			i = i + 1
		
		palyr = QgsPalLayerSettings()
		palyr.readFromLayer(vlI)
		palyr.enabled = False
		palyr.fieldName = 'name'
		palyr.placement = QgsPalLayerSettings.OverPoint
		palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'10','')
		#palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'color.red','')
		palyr.writeToLayer(vlI)
		self.canvas.refresh()

		legend = self.iface.legendInterface()
		allLayersListNew = self.canvas.layers()
 		for getLayerNew in allLayersListNew:
			if str(getLayerNew.name()) == str(lyrTempLine):
				legend.setLayerVisible(getLayerNew, False)
				
		global mIDPDetails
		self.iface.mapCanvas().scene().removeItem(mIDPDetails)	
		global rbp
		self.iface.mapCanvas().scene().removeItem(rbp)		
		global mIDP
		self.iface.mapCanvas().scene().removeItem(mIDP)
		global rbIDP
		self.iface.mapCanvas().scene().removeItem(rbIDP)
		global r
		self.iface.mapCanvas().scene().removeItem(r)		
	except:
		e = sys.exc_info()#[0]
		print e


    def stepsUpIDP(self): # ****dil
	stepz = self.genMapStepsIDP() 
	#self.dlg.ui.txtFirstSteps.setText(stepz[0])
	#global n
	#n = 1
	global nowIDP
	nowIDP = nowIDP - 1
	global nIDP
	nIDP = nIDP - 1
	if nowIDP < 1:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[0])
		nIDP = 1
	if nowIDP == 1:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[0])
	if nowIDP == 2:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[1])
	if nowIDP == 3:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[2])
	if nowIDP == 4:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[3])
	if nowIDP == 5:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[4])
	if nowIDP == 6:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[5])
	#if nowIDP == 7:
		#self.dlg.ui.txtFirstSteps.setText(stepz[5])

	
		

    def stepsDownIDP(self): #**** dil
	#one, two, three, four, five, six, seven = self.genMapSteps()
	#curStep = self.dlg.ui.txtFirstSteps.toHtml()
	stepz = self.genMapStepsIDP()
	global nowIDP
	global nIDP
	nIDP = nIDP + 1
	
	if nIDP == 1:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[0])
		nowIDP = 1
	if nIDP == 2:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[1])
		nowIDP = 2
	if nIDP == 3:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[2])
		nowIDP = 3
	if nIDP == 4:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[3])
		nowIDP = 4
	if nIDP == 5:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[4])
		nowIDP = 5
	if nIDP == 6:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[5])
		nowIDP = 6
	if nIDP == 7:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[6])
		nowIDP = 7
	if nIDP > 7:
		self.dlg.ui.txtFirstStepsIDP.setText(stepz[6])
		nowIDP = 7

	#if str(curStep) == str(one):
	#	self.dlg.ui.txtFirstSteps.setText(two)
	#elif str(curStep) == str(two):
	#	self.dlg.ui.txtFirstSteps.setText(three)
	#elif str(curStep) == str(three):
	#	self.dlg.ui.txtFirstSteps.setText(four)
	#elif str(curStep) == str(four):
	#	self.dlg.ui.txtFirstSteps.setText(five)
	#elif str(curStep) == str(five):
	#	self.dlg.ui.txtFirstSteps.setText(six)
	#elif str(curStep) == str(six):
	#	self.dlg.ui.txtFirstSteps.setText(seven)
	#elif str(curStep) == str(seven):
	#	self.dlg.ui.txtFirstSteps.setText(seven)
 	#else:
	#	self.dlg.ui.txtFirstSteps.setText(one)

    def genMapStepsIDP(self): #**** dil
	steps = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>' 
	one = "<b>Step 1</b> : Load the " + clBl + "flood-hazard layer " + clBls + "and " + clBl + "buildings layer " + clBls
	two = "<b>Step 2</b> : Check whether a file with " + clR + ".keywords " + clRs + "extension, is available in each layer bundle "
	three = "<b>Step 3</b> : If (.keywords files) available, press on " + clBl + "Generate map for process " + clBls + "button to generate a " + clBl + "flood-safe " + clBls + "layer "
	four = "<b>Step 4</b> : If (.keywords files) " + clR + "not " + clRs + "available, select the " + clBl + "flood-hazard layer " + clBls + "and " + clBl + "buildings layer " + clBls + "from the drop downs and provide a name for the output shapefile "
	five = "<b>Step 5</b> : " + clR + "(If followed step 4) " + clRs + "press on " + clBl + "Generate map " + clBls + "button to generate a " + clBl + "flood-safe " + clBls + "layer "
	six = "<b>Step 6</b> : The generated " + clBl + "flood-safe " + clBls + "layer will be automatically loaded to the TOC and will be saved in your " + clBl + "/home " + clBls + "directory "
	seven = clR + "<b><h3>Now you can start</h3></b> " + clRs  	

	self.dlg.ui.txtFirstStepsIDP.clear()	
	steps.append(one)
	steps.append(two)
	steps.append(three)
	steps.append(four)
	steps.append(five)
	steps.append(six)
	steps.append(seven)
	
	#return one, two, three, four, five, six, seven
	return steps

    def IDPTypeSelect(self):
	global IDP1
	IDP1 = ''
	global IDP2
	IDP2 = ''
	typegett = self.dlg.ui.cmbIDPcams.currentText()
	typeget = str(typegett)
	if  typeget== 'school':
		IDP1 = 'school'
	elif typeget == 'temple':
		IDP1 = 'temple'
	elif typeget == 'place  of  worship':
		IDP1 = 'place_of_worship'
	elif typeget == 'School + place_of_worship':
		IDP1 = 'school'
		IDP2 = 'place_of_worship'
	elif typeget == 'School and temple':
		IDP1 = 'school'
		IDP2 = 'temple'
		


    def selectNonAffecIDP(self): #**** dil
	global fid		
	global IDPReport			
	global IDP1	
	global IDP2
	global buildin_safe_path
	IDPReport = []
	tb='<table style="width:500px"><tr><th width="250" align="left">Name</th><th></th><th width="160" align="left">Type</th><th></th><th width="100" align="left">Capacity</th></tr>'
	IDPReport.append( ['NAME', 'TYPE', 'CAPACITY'] )
	self.dlg.setdetailfill(tb)
	path = str(buildin_safe_path)
	sortcap = "capacity" 
	ID = str(sortcap)
	datasource = ogr.Open(str(path)) 
	layer = datasource.GetLayer(0) # Import layer 0 --> only works with shapefiles
	layerName = str( layer.GetName() )# Save the Layersname first
	
	#sql query
	layers = datasource.ExecuteSQL("SELECT * FROM %s ORDER BY %s DESC'" % (layerName, ID) )
	for i in range(0,layers.GetFeatureCount()):
		feat = layers.GetFeature(i)
		cap = feat.GetField('capacity')		
		name = feat.GetField('Name')
		ty = feat.GetField('type')
		#geom = feat.geometry()
		print "befor if"
		if ty == str(IDP1) or ty == str(IDP2):
			name = self.getFieldIDPName(self.cLayer)
			cap = self.getFieldIDPCapacity(self.cLayer)
			BType = feat.GetField('type')
			BName = feat.GetField('Name')
			BCapacity = feat.GetField('capacity')
			a=str(BType)
			b=str(BName)
			c=str(BCapacity)
			self.dlg.listdetailfill('<tr><td width="250">' + b + '</td><td></td><td width="160">' + a + '</td><td></td><td width="100">' + c + '</td></tr>')	
			IDPReport.append( [str(BType), str(BName),str(BCapacity)] )
			print "end if"

	global countIDP
	countIDP = 0
	self.cLayer = self.canvas.currentLayer()
	i = 0
	global mIDPLocAll
	mIDPLocAll = []
	for feature in self.cLayer.getFeatures():
		buildType = self.getFieldIDPType(self.cLayer) 						
		Type = feature[buildType]
		geom = feature.geometry()
		global IDP1
		global IDP2
		print str(IDP1)
		print str(IDP2)
		if Type == str(IDP1) or Type == str(IDP2):
			fid=feature.id()
			point = geom.asPoint()
			print point
			mIDPLoc = "loc " + str(i)
	       		mIDPLoc = QgsVertexMarker(self.canvas)
	       		mIDPLoc.setCenter(point)
	       		mIDPLoc.setColor(QColor(0,255,0))
	       		mIDPLoc.setIconSize(6)
                    	mIDPLoc.setIconType(QgsVertexMarker.ICON_BOX)
                       	mIDPLoc.setPenWidth(5)
			countIDP = countIDP + 1
			i = i + 1
			mIDPLocAll.append(mIDPLoc)

    def LableIDPfeatures(self):
	#global palyr
	layerr = self.iface.mapCanvas().currentLayer()
	#layerLbll = self.getLayerByName(layerr) 						
	showFieldd ='capacity' 
	palyr = QgsPalLayerSettings()
	palyr.readFromLayer(layerr)
	palyr.enabled = True #False
	palyr.fieldName = showFieldd
	palyr.placement = QgsPalLayerSettings.AroundPoint
	palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
	#palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
	palyr.writeToLayer(layerr)
	self.iface.mapCanvas().refresh()

    def getFieldIDPName(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldIDPName = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "name"
			words = colHeadLower.split()
			if term in words:
				fieldIDPName = colHead
			d = d + 1
		if fieldIDPName == '':
			fieldIDPName = str(fields.field(0).name())
		return fieldIDPName

    def getFieldIDPType(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldIDPType = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "type"
			words = colHeadLower.split()
			if term in words:
				fieldIDPType = colHead
			d = d + 1
		if fieldIDPType == '':
			fieldIDPType = str(fields.field(1).name())
		return fieldIDPType

    def getFieldIDPCapacity(self, layer):
		fields = layer.pendingFields()
		fCount = fields.count()
		d = 0
		fieldIDPCap = ''
		while d < fCount:
			colHead = str(fields.field(d).name())
			colHeadLower = colHead.lower()
			for c in string.punctuation:
				colHeadLower= colHeadLower.replace(c," ")
			term = "capacity"
			words = colHeadLower.split()
			if term in words:
				fieldIDPCap = colHead
			d = d + 1
		if fieldIDPCap == '':
			fieldIDPCap = str(fields.field(2).name())
		return fieldIDPCap


    def selectIDPLoc(self):
	print "come"
	self.labelPos.clear()
	global stopPlace
	stopPlace = 1	
	self.place()
     #if (state==Qt.Checked):
             # connect to click signal
      	QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownIDPLoc)
             # connect our select function to the canvasClicked signal
        QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownIDPName)
     #else:
             # disconnect from click signal
             #QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDown)
             # disconnect our select function to the canvasClicked signal
             #QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeature)  



    def handleMouseDownIDPLoc(self, point, button):
        #global val
        #val = 3
	#print "handle"
	self.labelPos.clear()
        cLayer = self.canvas.currentLayer()
	cLayer.removeSelection()
	self.dlg.ui.txtLocNameIDP.clear()
        self.dlg.ui.txtLocNameIDP.setText( "<b>X :</b> "+str(point.x()) + " , <b>Y</b> : " +str(point.y()) )
	global xIDP
	global yIDP		
	xIDP=float(str(point.x()))
	yIDP=float(str(point.y()))		

	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownIDPLoc)

    def handleMouseDownIDPName(self, point, button):
       #global val
       #val = 3
       #print "selct"
       #QMessageBox.information( self.iface.mainWindow(),"Info", "in selectFeature function" )
       # setup the provider select to filter results based on a rectangle
       pntGeom = QgsGeometry.fromPoint(point)
       # scale-dependent buffer of 2 pixels-worth of map units
       pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       rect = pntBuff.boundingBox()
       # get currentLayer and dataProvider
       cLayer = self.canvas.currentLayer()
       selectList = []
       if cLayer:
	       self.markStartIDP()
               provider = cLayer.dataProvider()
               feat = QgsFeature()
               # create the select statement
               #provider.select([],rect) # the arguments mean no attributes returned, and do a bbox filter with our buffered rectangle to limit the amount of features
               #print "comee1"
	       request = QgsFeatureRequest().setFilterRect(rect)
	       #while provider.nextFeature(feat):
               #while cLayer.getFeatures(request).next():
	       #print "comee2"
	       for feature in cLayer.getFeatures(request):
		       #print "comee"
                       # if the feat geom returned from the selection intersects our point then put it in a list
                       #if feat.geometry().intersects(pntGeom):
 	       #feature = cLayer.getFeatures(request).next()
	               feature = cLayer.getFeatures(request).next()
               #ERROR***********************************************************************
	       #selectList.append(feature.id())
	               global fidIDP
                       fidIDP=feature.id()
	       #selectList[0]=feature.id()IDP
	       #QMessageBox.information( self.iface.mainWindow(),"Info", str(feature.id()) )
               #if self.selectList:
                       # make the actual selection
               #self.cLayer.setSelectedFeatures(self.selectList)
	       #self.cLayer.select(self.selectList)
	               #self.cLayer.select(fid)
		
		       #mark vertex (selection)
		       #global x1
		       #global y1
		       #global m1
		       #m1 = QgsVertexMarker(self.canvas)
		       #m1.setCenter(QgsPoint(x1,y1))
		       #m1.setColor(QColor(0,255,0))
		       #m1.setIconSize(6)
                       #m1.setIconType(QgsVertexMarker.ICON_BOX) # ICON_CROSS, ICON_X
                       #m1.setPenWidth(5)
                       # update the TextBrowser
	       #QMessageBox.information( self.iface.mainWindow(),"Info", "in selectFeature function" )
                       self.updateTextBrowserIDP()

       else:
               QMessageBox.information( self.iface.mainWindow(),"Info", "No layer currently selected in TOC" )    

    def markStartIDP(self):
	global xIDP
	global yIDP
	global mIDP
	mIDP = QgsVertexMarker(self.canvas)
	mIDP.setCenter(QgsPoint(xIDP,yIDP))
	mIDP.setColor(QColor(0,255,0))
	mIDP.setIconSize(6)
        mIDP.setIconType(QgsVertexMarker.ICON_BOX) # ICON_CROSS, ICON_X
        mIDP.setPenWidth(5)


    def updateTextBrowserIDP(self):
    	# if we have a selected feature
    	#if self.selectList:
	global fidIDP
        if(fidIDP!=0):
		cLayer = self.canvas.currentLayer()
            	self.provider = cLayer.dataProvider()
		#QMessageBox.information( self.iface.mainWindow(),"Info", "in updatetext function" )
        	# find the index of the 'NAME' column, branch if has one or not
        	##nIndx = self.provider.fieldNameIndex('NAME')
        	# get our selected feature from the provider, but we have to pass in an empty feature and the column index we want
        	#sFeat = QgsFeature()
        #if self.provider.featureAtId(self.selectList[0], sFeat, True, [nIndx]):
            # only if we have a 'NAME' column
		request = QgsFeatureRequest().setFilterFid(fidIDP)
		feature = cLayer.getFeatures(request).next()
                self.dlg.ui.txtLocCodiIDP.clear()
		fields = cLayer.pendingFields()
		boldOpp = '<b>'
		boldCll = '</b>'
		##firstCol = boldOpp + str(fields.field(0).name()) + boldCll + " : " + str(feature[0])
            	##if nIndx != -1:
                # get the feature attributeMap
                #attMap = sFeat.attributeMap()
                # clear old TextBrowser values
		#request = QgsFeatureRequest().setFilterFid(self.selectList[0])
		#cLayer = self.canvas.currentLayer()		
		#self.cLayer = iface.currentLayer()
		fieldNm = self.getFieldName(cLayer)
	   	featrGot = feature[fieldNm]
		featr = str(fieldNm) + " : " + str(featrGot)   

		global startNameIDP
		startNameIDP = "<b>Location</b> : " + str(featr)
                # now update the TextBrowser with attributeMap[nameColumnIndex]
                # when we first retrieve the value of 'NAME' it comes as a QString so we have to cast it to a Python string
                #self.dlg.setTextBrowserDesStart( str( attMap[nIndx].toString() ))
		#else:
			#global startName
			#startName = str(firstCol)			
		self.dlg.ui.txtLocCodiIDP.setText(str(startNameIDP))
		# disconnect our select function to the canvasClicked signal
        	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownIDPName)

    def disRangeIDPIndexChanged(self):
	global rangeIDP	
	rIDP = int(str(self.dlg.ui.cboDisRange.currentText()))
	rIDP = rIDP * 1000
	if rIDP == 1000:
		rangeIDP = 1000
	elif rIDP == 2000:
		rangeIDP = 2000
	elif rIDP == 3000:
		rangeIDP = 3000
	elif rIDP == 5000:
		rangeIDP = 5000
	elif rIDP == 8000:
		rangeIDP = 8000
	elif rIDP == 10000:
		rangeIDP = 10000
	else:
		rangeIDP = 2000

    def findNearbyIDP(self):
	global rangeIDP
	point = []
	global rbIDPAll
	rbIDPAll = []
	vl = self.canvas.currentLayer()
	director = QgsLineVectorLayerDirector( vl, -1, '','', '', 3 )
	properter = QgsDistanceArcProperter()
	director.addProperter( properter )
	crs = self.canvas.mapRenderer().destinationCrs()
	builder = QgsGraphBuilder( crs )
	global xIDP
	global yIDP
	global rbp	
	pStart = QgsPoint( xIDP, yIDP )
	delta = self.canvas.getCoordinateTransform().mapUnitsPerPixel() * 1
	rbp = QgsRubberBand( self.canvas)
	rbp.setColor( Qt.blue )
	rbp.addPoint( QgsPoint( pStart.x() - delta, pStart.y() - delta))
	rbp.addPoint( QgsPoint( pStart.x() + delta, pStart.y() - delta))
	rbp.addPoint( QgsPoint( pStart.x() + delta, pStart.y() + delta))
	rbp.addPoint( QgsPoint( pStart.x() - delta, pStart.y() + delta))
	
	tiedPoints = director.makeGraph( builder, [ pStart ] )
	graph = builder.graph()
	tStart = tiedPoints[ 0 ]
	idStart = graph.findVertex( tStart )
	( tree, cost ) = QgsGraphAnalyzer.dijkstra( graph, idStart, 0 )
	upperBound = []
	r = rangeIDP
	i = 0
	while i < len(cost):
		if cost[ i ] > r and tree[ i ] != -1:
			outVertexId = graph.arc( tree [ i ] ).outVertex()
			if cost[ outVertexId ] < r:
				upperBound.append( i )
		i = i + 1
	co = 0	
	for i in upperBound:
		centerPoint = graph.vertex( i ).point()
		#print centerPoint
		co = co + 1
		point.append(centerPoint)
		global rbIDP
		rbIDP = "rub " + str(co)
		rbIDP = QgsRubberBand( self.canvas, True )
		rbIDP.setColor( Qt.red )
		#rb.setIconSize(6)
        	#rb.setIconType(QgsVertexMarker.ICON_BOX) # ICON_CROSS, ICON_X
        	rbIDP.setWidth(10)
		rbIDP.addPoint( QgsPoint( centerPoint.x() - delta, centerPoint.y()-delta))
		rbIDP.addPoint( QgsPoint( centerPoint.x() + delta, centerPoint.y()-delta))
		rbIDP.addPoint( QgsPoint( centerPoint.x() + delta, centerPoint.y()+delta))
		rbIDP.addPoint( QgsPoint( centerPoint.x() - delta, centerPoint.y()+delta))
		rbIDPAll.append(rbIDP)
	
	j = 0
	while j < co-1:
		x1 = point[j]
		x2 = point[j + 1]
		j = j + 1
		#layer = QgsVectorLayer('Point','points',"memory")
		#pr = layer.dataProvider()
		#pt = QgsFeature()
		point1 = QgsPoint(x1)
		#pt.setGeometry(QgsGeometry.fromPoint(point1))
		#pr.addFeatures([pt])
		#layer.updateExtents()
		#pt = QgsFeature()
		point2 = QgsPoint(x2)
		#pt.setGeometry(QgsGeometry.fromPoint(point2))
		#pr.addFeatures([pt])
		#layer.updateExtents()
		#QgsMapLayerRegistry.instance().addMapLayers([layer])
		##layer = QgsVectorLayer('LineString','line',"memory")
		##pr = layer.dataProvider()
		##line = QgsFeature()
		#crs = core.QgscoordinateReferenceSystem(4326)
		#self.canvas.mapRenderer().setDestinationCrs(crs)		
		##line.setGeometry(QgsGeometry.fromPolyline([point1,point2]))
		##pr.addFeatures([line])
		##layer.updateExtents()
		##QgsMapLayerRegistry.instance().addMapLayers([layer])
		global r
		r = QgsRubberBand(self.canvas, False) # False = not a polygon
		points = [ point1,pStart ]
		r.setToGeometry(QgsGeometry.fromPolyline(points), None)

	global lyrTempLine
	lyrTempLine = 'line'
	layer = QgsVectorLayer('LineString?crs=epsg:4326','line',"memory")
	pr = layer.dataProvider()
	line = QgsFeature()		
	line.setGeometry(QgsGeometry.fromPolyline([point[co-1],point[0]]))
	pr.addFeatures([line])
	layer.updateExtents()
	QgsMapLayerRegistry.instance().addMapLayers([layer])

	#vpoly = QgsVectorLayer("Polygon?crs=epsg:4326", "pointbuffer", "memory")
	#feature = QgsFeature()
	#print "commmmmm"
	#feature.setGeometry( QgsGeometry.fromPoint(QgsPoint( xIDP, yIDP )).buffer(100,5))
	#provider = vpoly.dataProvider()
	#vpoly.startEditing()
	#provider.addFeatures( [feature] )
	#vpoly.updateExtents()
	#QgsMapLayerRegistry.instance().addMapLayers([vpoly])
	#vpoly.commitChanges()
	

    def viewIDPDetails(self):
	self.labelPos.clear()
	global stopPlace
	stopPlace = 1	
	self.place()
	QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownIDPDetails)


    def handleMouseDownIDPDetails(self, point, button):
       global xIDPDetails
       global yIDPDetails		
       xIDPDetails=float(str(point.x()))
       yIDPDetails=float(str(point.y()))
       global pointIDPSel
       pointIDPSel = point		

       pntGeom = QgsGeometry.fromPoint(point)
       # scale-dependent buffer of 2 pixels-worth of map units
       pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       rect = pntBuff.boundingBox()
       # get currentLayer and dataProvider
       cLayer = self.canvas.currentLayer()
       selectList = []
       if cLayer:
	       self.markStrtIDPDetails()
               provider = cLayer.dataProvider()
               feat = QgsFeature()
               # create the select statement
               #provider.select([],rect) # the arguments mean no attributes returned, and do a bbox filter with our buffered rectangle to limit the amount of features
               #print "comee1"
	       request = QgsFeatureRequest().setFilterRect(rect)
	       #while provider.nextFeature(feat):
               #while cLayer.getFeatures(request).next():
	       #print "comee2"
	       for feature in cLayer.getFeatures(request):
		       #print "comee"
                       # if the feat geom returned from the selection intersects our point then put it in a list
                       #if feat.geometry().intersects(pntGeom):
 	       #feature = cLayer.getFeatures(request).next()
	               feature = cLayer.getFeatures(request).next()
               #ERROR***********************************************************************
	       #selectList.append(feature.id())
	               global fidIDPDetails
                       fidIDPDetails=feature.id()
	       #selectList[0]=feature.id()IDP
	       #QMessageBox.information( self.iface.mainWindow(),"Info", str(feature.id()) )
               #if self.selectList:
                       # make the actual selection
               #self.cLayer.setSelectedFeatures(self.selectList)
	       #self.cLayer.select(self.selectList)
	               #self.cLayer.select(fid)
		
		       #mark vertex (selection)
		       #global x1
		       #global y1
		       #global m1
		       #m1 = QgsVertexMarker(self.canvas)
		       #m1.setCenter(QgsPoint(x1,y1))
		       #m1.setColor(QColor(0,255,0))
		       #m1.setIconSize(6)
                       #m1.setIconType(QgsVertexMarker.ICON_BOX) # ICON_CROSS, ICON_X
                       #m1.setPenWidth(5)
                       # update the TextBrowser
	       #QMessageBox.information( self.iface.mainWindow(),"Info", "in selectFeature function" )
                       self.updateTextBrowserIDPDetails()

       else:
               QMessageBox.information( self.iface.mainWindow(),"Info", "No layer currently selected in TOC" )    

    def markStrtIDPDetails(self):
	global xIDPDetails
	global yIDPDetails
	global mIDPDetails
	mIDPDetails = QgsVertexMarker(self.canvas)
	mIDPDetails.setCenter(QgsPoint(xIDPDetails,yIDPDetails))
	mIDPDetails.setColor(QColor(0,0,255))
	mIDPDetails.setIconSize(6)
        mIDPDetails.setIconType(QgsVertexMarker.ICON_X) # ICON_CROSS, ICON_X
        mIDPDetails.setPenWidth(5)


    def showIDPLabel(self):
		global vlI
		global IDPSelName
		global pointIDPSel
		# create layer
		vlI = QgsVectorLayer("Point?crs=epsg:4326", "temporary_points", "memory")
		pr = vlI.dataProvider()
		# add fields
		vlI.startEditing()
		pr.addAttributes( [ QgsField("name", QVariant.String) ] )
		# add a feature
		fet = QgsFeature()
		fet.setGeometry( QgsGeometry.fromPoint( pointIDPSel ))
		fet.setAttributes([str(IDPSelName)])
		pr.addFeatures([fet])

		# update layer’s extent when new features have been added
		# because change of extent in provider is not propagated to the layer
		vlI.updateExtents()
		vlI.commitChanges()
		#verify layer craeted
		print "fields:", len(pr.fields())
		print "features:", pr.featureCount()
		f = QgsFeature()
		features = vlI.getFeatures()
		for f in features:
			print "F:",f.id(), f.attributes(), f.geometry().asPoint()
		QgsMapLayerRegistry.instance().addMapLayer(vlI)

		palyr = QgsPalLayerSettings()
		palyr.readFromLayer(vlI)
		palyr.enabled = True
		palyr.fieldName = 'name'
		palyr.placement = QgsPalLayerSettings.OverPoint
		palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'10','')
		#palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'color.red','')
		palyr.writeToLayer(vlI)
		self.canvas.refresh()



    def updateTextBrowserIDPDetails(self):
	self.labelPos.clear()
    	# if we have a selected feature
    	#if self.selectList:
	global fidIDPDetails
        if(fidIDPDetails!=0):
		cLayer = self.canvas.currentLayer()
            	self.provider = cLayer.dataProvider()
		request = QgsFeatureRequest().setFilterFid(fidIDPDetails)
		feature = cLayer.getFeatures(request).next()
                self.dlg.ui.txtNearIDPDetails.clear()
		fields = cLayer.pendingFields()
		boldOpp = '<b>'
		boldCll = '</b>'

		fCountt = fields.count()
		d = 0
		while d < fCountt:
			colHd = str(fields.field(d).name())
			Col = boldOpp + str(colHd) + boldCll + " : " + str(feature[colHd]) + "\n"
			self.dlg.ui.txtNearIDPDetails.append(str(Col))
			#self.dlg.ui.txtNearIDPDetails.append("\n")
			d = d + 1
		

		#Col = boldOpp + str(fields.field(0).name()) + boldCll + " : " + str(feature[0])
            	##if nIndx != -1:
                # get the feature attributeMap
                #attMap = sFeat.attributeMap()
                # clear old TextBrowser values
		#request = QgsFeatureRequest().setFilterFid(self.selectList[0])
		cLayer = self.iface.mapCanvas().currentLayer()		
		#self.cLayer = iface.currentLayer()
		fieldNm = self.getFieldName(cLayer)
	   	featrGot = feature[fieldNm]
		#featr = str(fieldNm) + " : " + str(featrGot)
		global IDPSelName
		IDPSelName = str(featrGot)		   

		#global startNameIDP
		#startNameIDP = "<b>Location</b> : " + str(featr)
                # now update the TextBrowser with attributeMap[nameColumnIndex]
                # when we first retrieve the value of 'NAME' it comes as a QString so we have to cast it to a Python string
                #self.dlg.setTextBrowserDesStart( str( attMap[nIndx].toString() ))
		#else:
			#global startName
			#startName = str(firstCol)			
		#self.dlg.ui.txtNearIDPDetails.setText(str(startNameIDP))
		# disconnect our select function to the canvasClicked signal
        	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownIDPDetails)
		self.showIDPLabel()



    #keywords
    def generateMapIDP(self):
	try:
		self.keywords_from_layersIDP()
	except:
		e = sys.exc_info()[0]
		print e
		colR = '<font color="red">'
		colRs = '</font>'	
		textToShow = "Sorry. No " + colR + ".keywords " + colRs + "files found" 
		textSub = "Please select the relevant layers from drop downs and generate map manually"
		msgBox = QtGui.QMessageBox()
 		msgBox.setText(str(textToShow))
 		msgBox.setInformativeText(str(textSub))
 		msgBox.setStandardButtons(QMessageBox.Ok)
		msgBox.setWindowTitle("No Keywords Found Error")
 		ret = msgBox.exec_();


    def generateMapManuallyIDP(self):
#	allLayersLoaded = self.canvas.layers()
# 	for SelLayer in allLayersLoaded:	
#		self.dlg.ui.cboIDPLayer.addItem(SelLayer.name())
#                self.dlg.ui.cboFloodLayerIDP.addItem(SelLayer.name())
	global IDPSafePathManu	
	IDPLayer = self.dlg.ui.cboIDPLayer.currentText()	
	global floodLayer
	global IDPPath
	global fdPathIDP
	global buildin_safe_path
	floodLayer = self.dlg.ui.cboFloodLayerIDP.currentText()
	outputFile = self.dlg.ui.leOutputFileIDP.text()
	allLayersList = self.canvas.layers()
 	for getLayer in allLayersList:
		if str(getLayer.name()) == str(IDPLayer):
			IDPPath = str(getLayer.source())
		elif str(getLayer.name()) == str(floodLayer):
			fdPathIDP = str(getLayer.source())
	output = os.path.splitext(IDPPath)[0]
	output += '_'+outputFile+'.shp'
	IDPSafePathManu = output
	buildin_safe_path = output
	##processing.runandload("qgis:difference", rdPath, fdPath, output)
	processing.runalg("qgis:difference", IDPPath, fdPathIDP, output)
	wb = QgsVectorLayer(output, outputFile, 'ogr')
	
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
	else:
		print "No layer found"

	#active new layer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		if str(getLayerNew.name()) == str(outputFile):
			legend.setLayerVisible(getLayerNew, True)
		elif str(getLayerNew.name()) == str(floodLayer):
			legend.setLayerVisible(getLayerNew, True)
		else: 
			legend.setLayerVisible(getLayerNew, False)
	

	
    def clearGenMapFieldsIDP(self):
	self.dlg.ui.leOutputFileIDP.clear()
	self.dlg.ui.cboIDPLayer.clear()
        self.dlg.ui.cboFloodLayerIDP.clear()

	allLayersIn = self.canvas.layers()
 	for LayerNow in allLayersIn:	
		self.dlg.ui.cboIDPLayer.addItem(LayerNow.name())
                self.dlg.ui.cboFloodLayerIDP.addItem(LayerNow.name())
	colRd = '<font color="red">'
	colRds = '</font>'
	self.dlg.ui.txtFirstStepsIDP.clear()
	self.dlg.ui.txtFirstStepsIDP.setText(colRd + "<b>Please follow these steps</b>" + colRds + '\n' + "<b>(Press on down arrow to start)</b>")
	global nIDP
	nIDP = 0
	global nowIDP
	nowIDP = 2



    def keywords_from_layersIDP(self): #**** dil
	allLayers = self.canvas.layers()
 	for oneLayer in allLayers:	
		self.layer = oneLayer
		self.load_state_from_keywordsIDP()
	global layer_path_haz
	global buildinLayer
	global layer_path_build
	global buildin_safe_path
	global IDPSafePathManu
	result_file_path = os.path.splitext(layer_path_build)[0]
        result_file_path += '_flood_affect.shp'
	buildin_safe_path = result_file_path
	IDPSafePathManu = result_file_path 
	processing.runalg("qgis:difference", layer_path_build, layer_path_haz, result_file_path)
	wb = QgsVectorLayer(result_file_path, 'IDP_safe', 'ogr')
	buildinLayer = wb
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
	else:
		print "No layer found"

	#active New Layer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
	outFile = 'IDP_safe'
 	for getLayerNew in allLayersListNew:
		if str(getLayerNew.name()) == str(outFile):
			legend.setLayerVisible(getLayerNew, True)
		elif str(getLayerNew.source()) == str(layer_path_haz):
			legend.setLayerVisible(getLayerNew, True)
		else: 
			legend.setLayerVisible(getLayerNew, False)
	
	global source

    def set_layerIDP(self): #**** dil
        """Set the layer associated with the keyword editor.

        :param layer: Layer whose keywords should be edited.
        :type layer: QgsMapLayer
        """
        #self.layer = layer
	self.layer = self.canvas.currentLayer()
        self.load_state_from_keywordsIDP()

    def on_radExposure_toggled(self, theFlag): #****dil
        """Automatic slot executed when the hazard radio is toggled on.

        :param theFlag: Flag indicating the new checked state of the button.
        :type theFlag: bool
        """
        if not theFlag:
            return
        self.set_category('exposure')
        self.update_controls_from_listIDP()

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('bool')

    def on_pbnRemove_clicked(self): #****dil
        """Automatic slot executed when the pbnRemove button is pressed.

        Any selected items in the keywords list will be removed.
        """
        for item in self.lstKeywords.selectedItems():
            self.lstKeywords.takeItem(self.lstKeywords.row(item))
        self.leKey.setText('')
        self.leValue.setText('')
        self.update_controls_from_listIDP()

    def set_category(self, category): #****dil
        """Set the category radio button based on category.

        :param category: Either 'hazard', 'exposure' or 'postprocessing'.
        :type category: str

        :returns: False if radio button could not be updated, otherwise True.
        :rtype: bool
        """
        # convert from QString if needed
        category = str(category)
#        if self.get_value_for_key('category') == category:
            #nothing to do, go home
#            return True
        if category not in ['hazard', 'exposure', 'postprocessing']:
            # .. todo:: report an error to the user
            return False
            # Special case when category changes, we start on a new slate!

        if category == 'hazard':
            # only cause a toggle if we actually changed the category
            # This will only really be apparent if user manually enters
            # category as a keyword
            self.resetIDP()
            #self.dlg.ui.radHazardIDP.blockSignals(True)
            #self.dlg.ui.radHazardIDP.setChecked(True)
            #self.dlg.ui.radHazardIDP.blockSignals(False)
            #self.remove_item_by_key('subcategory')
            #self.remove_item_by_key('datatype')
            self.add_list_entry('category', 'hazard')
            hazard_list = self.standard_hazard_list
            self.set_subcategory_list(hazard_list)

        elif category == 'exposure':
            self.resetIDP()
            #self.dlg.ui.radExposureIDP.blockSignals(True)
            #self.dlg.ui.radExposureIDP.setChecked(True)
            #self.dlg.ui.radExposureIDP.blockSignals(False)
            #self.remove_item_by_key('subcategory')
            #self.remove_item_by_key('unit')
            self.add_list_entry('category', 'exposure')
            exposure_list = self.standard_exposure_list
            self.set_subcategory_list(exposure_list)

        else:
            self.resetIDP()
            self.radPostprocessing.blockSignals(True)
            self.radPostprocessing.setChecked(True)
            self.radPostprocessing.blockSignals(False)
            #self.remove_item_by_key('subcategory')
            self.add_list_entry('category', 'postprocessing')

        return True

    def resetIDP(self, primary_keywords_only=True): #** dil
        """Reset all controls to a blank state.

        :param primary_keywords_only: If True (the default), only reset
            Subcategory, datatype and units.
        :type primary_keywords_only: bool
        """

        #self.dlg.ui.leSubcategoryIDP.clear()
       # self.dlg.ui.leTitleIDP.clear()
        #self.dlg.ui.leSourceIDP.clear()
	#self.dlg.ui.radExposureIDP.setChecked(True)
	self.dlg.ui.lblLayerNameIDP.clear()

    def load_state_from_keywordsIDP(self): #**** dil
        """Set the ui state to match the keywords of the active layer.

        In case the layer has no keywords or any problem occurs reading them,
        start with a blank slate so that subcategory gets populated nicely &
        we will assume exposure to start with.

        Also if only title is set we use similar logic (title is added by
        default in dock and other defaults need to be explicitly added
        when opening this dialog). See #751

        """
        keywords = {'category': 'exposure'}

        try:
            # Now read the layer with sub layer if needed
            keywords = self.keyword_io.read_keywords(self.layer)
        except (InvalidParameterError,
                HashNotFoundError):
                #NoKeywordsFoundError):
            pass

        layer_name = self.layer.name()
        #if 'title' not in keywords:
        #self.dlg.ui.leTitleIDP.setText(self.layer.name())
	#print self.layer.name()
        self.dlg.ui.lblLayerNameIDP.setText('Keywords for %s' % self.layer.name())

        #if 'source' in keywords:
	    #print str(keywords['source'])
            #self.dlg.ui.leSourceIDP.setText(str(keywords['source']))
       # else:
	    #print "come"
            #self.dlg.ui.leSourceIDP.setText('')

        # if we have a category key, unpack it first
        # so radio button etc get set
        if 'category' in keywords:
            self.set_category(keywords['category'])
            keywords.pop('category')
        else:
            # assume exposure to match ui. See issue #751
            self.add_list_entry('category', 'exposure')

        for key in keywords.iterkeys():
            self.add_list_entry(key, str(keywords[key]))

	if 'subcategory' in keywords:
            self.set_category(keywords['subcategory'])
	    #self.dlg.ui.leSubcategoryIDP.setText(keywords['subcategory'])
	
	if str(keywords['subcategory']) == 'flood':
	    #print "come1"
	    global layer_path_haz
	    layer_path_haz = str(self.layer.source())
	    #print layer_path_haz

	elif str(keywords['subcategory']) == 'structure':
            #print "come2"
	    global layer_path_build
	    layer_path_build = str(self.layer.source())
            #print layer_path_rd	

	#print layer_path_haz
	#print layer_path_rd
        # now make the rest of the safe_qgis reflect the list entries
        self.update_controls_from_listIDP()

    def update_controls_from_listIDP(self): #***dil
        """Set the ui state to match the keywords of the active layer."""
        if self.layer is not None:
            layer_name = self.layer.name()
	    #self.dlg.ui.leTitleIDP.setText(self.layer.name())
            self.dlg.ui.lblLayerNameIDP.setText('Keywords for %s' % layer_name)
        else:
            self.dlg.ui.lblLayerNameIDP.setText('')

        self.toggle_postprocessing_widgets()

        self.resize_dialog()

    def refreshIDP(self): #*** dil
	self.set_layerIDP()



    ##**********************************************************************dil IDP above**************************************************************

    def stepsUp(self):
	stepz = self.genMapSteps() 
	#self.dlg.ui.txtFirstSteps.setText(stepz[0])
	#global n
	#n = 1
	global now
	now = now - 1
	global n
	n = n - 1
	if now < 1:
		self.dlg.ui.txtFirstSteps.setText(stepz[0])
		n = 1
	if now == 1:
		self.dlg.ui.txtFirstSteps.setText(stepz[0])
	if now == 2:
		self.dlg.ui.txtFirstSteps.setText(stepz[1])
	if now == 3:
		self.dlg.ui.txtFirstSteps.setText(stepz[2])
	if now == 4:
		self.dlg.ui.txtFirstSteps.setText(stepz[3])
	if now == 5:
		self.dlg.ui.txtFirstSteps.setText(stepz[4])
	if now == 6:
		self.dlg.ui.txtFirstSteps.setText(stepz[5])
	#if now == 7:
		#self.dlg.ui.txtFirstSteps.setText(stepz[5])

	
		

    def stepsDown(self):
	#one, two, three, four, five, six, seven = self.genMapSteps()
	#curStep = self.dlg.ui.txtFirstSteps.toHtml()
	stepz = self.genMapSteps()
	global now
	global n
	n = n + 1
	
	if n == 1:
		self.dlg.ui.txtFirstSteps.setText(stepz[0])
		now = 1
	if n == 2:
		self.dlg.ui.txtFirstSteps.setText(stepz[1])
		now = 2
	if n == 3:
		self.dlg.ui.txtFirstSteps.setText(stepz[2])
		now = 3
	if n == 4:
		self.dlg.ui.txtFirstSteps.setText(stepz[3])
		now = 4
	if n == 5:
		self.dlg.ui.txtFirstSteps.setText(stepz[4])
		now = 5
	if n == 6:
		self.dlg.ui.txtFirstSteps.setText(stepz[5])
		now = 6
	if n == 7:
		self.dlg.ui.txtFirstSteps.setText(stepz[6])
		now = 7
	if n > 7:
		self.dlg.ui.txtFirstSteps.setText(stepz[6])
		now = 7

	#if str(curStep) == str(one):
	#	self.dlg.ui.txtFirstSteps.setText(two)
	#elif str(curStep) == str(two):
	#	self.dlg.ui.txtFirstSteps.setText(three)
	#elif str(curStep) == str(three):
	#	self.dlg.ui.txtFirstSteps.setText(four)
	#elif str(curStep) == str(four):
	#	self.dlg.ui.txtFirstSteps.setText(five)
	#elif str(curStep) == str(five):
	#	self.dlg.ui.txtFirstSteps.setText(six)
	#elif str(curStep) == str(six):
	#	self.dlg.ui.txtFirstSteps.setText(seven)
	#elif str(curStep) == str(seven):
	#	self.dlg.ui.txtFirstSteps.setText(seven)
 	#else:
	#	self.dlg.ui.txtFirstSteps.setText(one)

    def genMapSteps(self):
	steps = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>' 
	one = "<b>Step 1</b> : Load the " + clBl + "flood-hazard layer " + clBls + "and " + clBl + "road-network layer " + clBls
	two = "<b>Step 2</b> : Check whether a file with " + clR + ".keywords " + clRs + "extension, is available in each layer bundle "
	three = "<b>Step 3</b> : If (.keywords files) available, press on " + clBl + "Generate map for process " + clBls + "button to generate a " + clBl + "flood-safe " + clBls + "layer "
	four = "<b>Step 4</b> : If (.keywords files) " + clR + "not " + clRs + "available, select the " + clBl + "flood-hazard layer " + clBls + "and " + clBl + "road-network layer " + clBls + "from the drop downs and provide a name for the output shapefile "
	five = "<b>Step 5</b> : " + clR + "(If followed step 4) " + clRs + "press on " + clBl + "Generate map " + clBls + "button to generate a " + clBl + "flood-safe " + clBls + "layer "
	six = "<b>Step 6</b> : The generated " + clBl + "flood-safe " + clBls + "layer will be automatically loaded to the TOC and will be saved in the same directory where the other loaded maps are saved "
	seven = clR + "<b><h3>Now you can start</h3></b> " + clRs  	

	self.dlg.ui.txtFirstSteps.clear()	
	steps.append(one)
	steps.append(two)
	steps.append(three)
	steps.append(four)
	steps.append(five)
	steps.append(six)
	steps.append(seven)
	
	#return one, two, three, four, five, six, seven
	return steps
	

    def refreshLayersHosp(self):
	#global rH
	#rH = 1 
	self.dlg.ui.cmbHospitalLayerR.clear()
	allLayersLoaded = self.canvas.layers()
 	for SelLayer in allLayersLoaded:	
		self.dlg.ui.cmbHospitalLayerR.addItem(SelLayer.name())
	#rH = 0

    def refreshLayersIDP(self):
	#global rI
	#rI = 1
	self.dlg.ui.cmbIDPCampLayerR.clear()
	allLayersLoaded = self.canvas.layers()
 	for SelLayer in allLayersLoaded:	
		self.dlg.ui.cmbIDPCampLayerR.addItem(SelLayer.name())

    def stopHospIndexChanged(self):
	try:
		# global rH
		# print rH
		global allHosp
		allHosp = []
		stopHosp = self.dlg.ui.cmbHospitalLayerR.currentText()
		# self.dlg.ui.cmbHospitalR.clear()
		if stopHosp != 'Select layer': #and rH == 0:
			global stopHospLayer
			stopHospLayer = self.getLayerByName( stopHosp )
			# print stopHospLayer
			# print stopHospLayer.name()
			global fieldNameHosp
			fieldNameHosp = self.getFieldName(stopHospLayer)
			buildType = self.getFieldIDPType(stopHospLayer)
			self.dlg.ui.cmbHospitalR.clear() 
			for feature in stopHospLayer.getFeatures():
				Type = feature[buildType]
				if Type == 'hospital':					
					name = feature[fieldNameHosp]
					if str(name) != 'NULL':
						allHosp.append(name)
						print "came here"
						# self.dlg.ui.cmbHospitalR.addItem(str(name))
						# self.checkPossibleHosp()
	except:
		e = sys.exc_info()[0]
		print e

    #def checkPossibleHospOk(self):
	#self.checkPossibleHosp()
	#print "Hello"	

    def checkPossibleHospOkk(self):
	print "Hello"

    def checkPossibleHospOk(self):
	global allHosp
	global stopHospLayer
	possibleHosp = []
	#show waiting gif
	print "movie"
	moviee = QtGui.QMovie(":/plugins/floogin/bar.gif")
	self.dlg.ui.lblWait.setVisible( True )
	self.dlg.ui.lblWait.setMovie(moviee)
	moviee.start()
	print "start"	
	fieldNameHosp = self.getFieldName(stopHospLayer)
	buildType = self.getFieldIDPType(stopHospLayer)
	countHos = 0
	for i in xrange(len(allHosp)):
		curHos = allHosp[i]
		print curHos
		for feature in stopHospLayer.getFeatures():
			Type = feature[buildType]
			if Type == 'hospital':					
				name = feature[fieldNameHosp]	
				if curHos == name:
					geom = feature.geometry()
					pointStopHosp = geom.asPoint()
					global x2
					global y2		
					x2=float(str(pointStopHosp.x()))
					y2=float(str(pointStopHosp.y()))
					##applying path finding function##
					vl=self.canvas.currentLayer()
					director = QgsLineVectorLayerDirector( vl, -1, '', '', '', 3 )
					properter = QgsDistanceArcProperter()
					director.addProperter( properter )
					# crs = qgis.utils.iface.mapCanvas().mapRenderer().destinationCrs()
					crs = self.canvas.mapRenderer().destinationCrs()
					builder = QgsGraphBuilder( crs )	
					global x1
					global y1
					pStart = QgsPoint( x1, y1 )
					pStop = QgsPoint( x2, y2 )
					tiedPoints = director.makeGraph( builder, [ pStart, pStop ] )
					#tiedPoints = director.makeGraph( builder, [ pStart ] )
					graph = builder.graph()
					tStart = tiedPoints[ 0 ]
					tStop = tiedPoints[ 1 ]
					idStart = graph.findVertex( tStart )
					idStop = graph.findVertex( tStop )
					( tree, cost ) = QgsGraphAnalyzer.dijkstra( graph, idStart, 0 )
					if tree[ idStop ] != -1: #check path availability
						pp = []
						curPos = idStop		
						while curPos != idStart:
							pp.append( graph.vertex( graph.arc( tree[ curPos ] ).inVertex() ).point() )
							curPos = graph.arc( tree[ curPos ] ).outVertex();
		
						pp.append( tStart )
						pcountt = 0
						pcountLbl = 0		
						for pnt in pp:
							#print pnt
							pcountt = pcountt +1	
						print pcountt
						pck = pcountt
						ppk = pp
						tot = 0.0
						while pck > 1 :
							pointt1 = QgsPoint(ppk[pck-1])			
							pointt2 = QgsPoint(ppk[pck-2])
							tot = tot + (self.distance(pointt1.x(), pointt1.y(), pointt2.x(), pointt2.y()))
							pck = pck - 1
						totDis = tot
						
						possibleHosp.append(curHos)
						possibleHosp.append(totDis)
						countHos = countHos + 1
						break
	if not possibleHosp:
		self.dlg.ui.lblNoHospReach.setVisible(True)
	else:
		print "unSorted"
		for d in xrange(len(possibleHosp)):
			print str(possibleHosp[d])		
		k = 0
		rdLen = []
		while k < len(possibleHosp):
			rdLen.append(float(possibleHosp[k+1]))
			k = k + 2
		
		#bubble sort
		#passs = 1
		#i = 0
		#while passs < countHos:
			#while i < countHos - passs:
				#if rdLen[i] > rdLen[i+1]:
					#temp = rdLen[i]
					#rdLen[i] = rdLen[i+1]
					#rdLen[i+1] = temp
				#i = i + 1
			#passs = passs + 1
		
		rdLen.sort()
		for dd in xrange(len(rdLen)):
			print str(rdLen[dd])		
		

		m = 0
		global possibleHospSorted
		possibleHospSorted = []
		while m < len(rdLen):
			cur = rdLen[m]
			n = 0
			while n < len(possibleHosp):
				now = possibleHosp[n+1]
				if cur == now:
					possibleHospSorted.append(str(possibleHosp[n]))
					possibleHospSorted.append(str(possibleHosp[n+1]))	
				n = n + 2
			m = m + 1

		print "sorted"
		for d in xrange(len(possibleHospSorted)):
			print str(possibleHospSorted[d])		

		self.dlg.ui.cmbHospitalR.clear()
		j = 0    		
		while j < len(possibleHospSorted):
			self.dlg.ui.cmbHospitalR.addItem(str(possibleHospSorted[j]))
			j = j + 2
	moviee.stop()
	self.dlg.ui.lblWait.setVisible( False )
	self.dlg.ui.btnshowDetailsHos.setVisible(True)
		

    def showHowDetailsHos(self):
	global possibleHospSorted
	global startName
	self.dlgResD.show()
	self.dlgResD.txtShowHow.clear()
	show = "Distance " + "<b>To</b>" + " non-affected Hospitals " + "<b>From</b> " + str(startName) 
	self.dlgResD.txtShowHow.setText(str(show))
	colHeads = '<table style="width:400px"><tr><th width="200" align="left">Hospital</th><th></th><th width="200" align="left">Distance(~km)</th></tr>'
	self.dlgResD.txtShowHow.append('')	
	self.dlgResD.txtShowHow.append( colHeads )
	j = 0    		
	while j < len(possibleHospSorted):
		values = '<tr><td width="200">' + str(possibleHospSorted[j]) + '</td><td></td><td width="200">' + str(round(float(possibleHospSorted[j+1]),2)) + '</td><td></td></tr>'
		self.dlgResD.txtShowHow.append( values )
		j = j + 2



    def stopIDPIndexChanged(self):
		try:
			#global rI
			global allIDP
			allIDP = []
			stopIDP = self.dlg.ui.cmbIDPCampLayerR.currentText()
			#self.dlg.ui.cmbIDPCampR.clear()
			if stopIDP != 'Select layer': #and rI == 0:
				global stopIDPLayer 
				stopIDPLayer = self.getLayerByName( stopIDP )
				#print stopIDPLayer
				#print stopIDPLayer.name()
				#print fieldName
				global fieldNameIDP 
				fieldNameIDP = self.getFieldName(stopIDPLayer)
				buildType = self.getFieldIDPType(stopIDPLayer)
				self.dlg.ui.cmbIDPCampR.clear() 
				for feature in stopIDPLayer.getFeatures(): 						
					Type = feature[buildType]
					if Type == 'school' or Type == 'place_of_worship' or Type =='temple':
						name = feature[fieldNameIDP]
						if str(name) != 'NULL':
							#self.dlg.ui.cmbIDPCampR.addItem(str(name))
							allIDP.append(str(name))
			#rI = 0
		except:
			e = sys.exc_info()[0]
			print e

    #def checkPossibleIDPOk(self):
	#self.checkPossibleIDP()	

    def checkPossibleIDPOk(self):
	#show waiting gif
	print "movie"
	movieee = QtGui.QMovie(":/plugins/floogin/bar.gif")
	self.dlg.ui.lblWait.setVisible( True )
	self.dlg.ui.lblWait.setMovie(movieee)
	movieee.start()
	print "start"	
	global allIDP
	global stopIDPLayer
	possibleIDP = []	
	fieldNameIDP = self.getFieldName(stopIDPLayer)
	buildType = self.getFieldIDPType(stopIDPLayer)
	countIDP = 0
	for i in xrange(len(allIDP)):
		curIDP = allIDP[i]
		#print curIDP
		for feature in stopIDPLayer.getFeatures():
			Type = feature[buildType]
			if Type == 'school' or Type == 'place_of_worship' or Type =='temple':					
				name = feature[fieldNameIDP]	
				if curIDP == name:
					geom = feature.geometry()
					pointStopIDP = geom.asPoint()
					global x2
					global y2		
					x2=float(str(pointStopIDP.x()))
					y2=float(str(pointStopIDP.y()))
					##applying path finding function##
					vl=self.canvas.currentLayer()
					director = QgsLineVectorLayerDirector( vl, -1, '', '', '', 3 )
					properter = QgsDistanceArcProperter()
					director.addProperter( properter )
					# crs = qgis.utils.iface.mapCanvas().mapRenderer().destinationCrs()
					crs = self.canvas.mapRenderer().destinationCrs()
					builder = QgsGraphBuilder( crs )	
					global x1
					global y1
					pStart = QgsPoint( x1, y1 )
					pStop = QgsPoint( x2, y2 )
					tiedPoints = director.makeGraph( builder, [ pStart, pStop ] )
					#tiedPoints = director.makeGraph( builder, [ pStart ] )
					graph = builder.graph()
					tStart = tiedPoints[ 0 ]
					tStop = tiedPoints[ 1 ]
					idStart = graph.findVertex( tStart )
					idStop = graph.findVertex( tStop )
					( tree, cost ) = QgsGraphAnalyzer.dijkstra( graph, idStart, 0 )
					if tree[ idStop ] != -1: #check path availability
						pp = []
						curPos = idStop		
						while curPos != idStart:
							pp.append( graph.vertex( graph.arc( tree[ curPos ] ).inVertex() ).point() )
							curPos = graph.arc( tree[ curPos ] ).outVertex();
		
						pp.append( tStart )
						pcountt = 0
						pcountLbl = 0		
						for pnt in pp:
							#print pnt
							pcountt = pcountt +1	
						#print pcountt
						pck = pcountt
						ppk = pp
						tot = 0.0
						while pck > 1 :
							pointt1 = QgsPoint(ppk[pck-1])			
							pointt2 = QgsPoint(ppk[pck-2])
							tot = tot + (self.distance(pointt1.x(), pointt1.y(), pointt2.x(), pointt2.y()))
							pck = pck - 1
						totDis = tot
						
						possibleIDP.append(curIDP)
						possibleIDP.append(totDis)
						countIDP = countIDP + 1
						break
	if not possibleIDP:
		self.dlg.ui.lblNoIDPReach.setVisible(True)
	else:
		print "unSorted"
		for d in xrange(len(possibleIDP)):
			print str(possibleIDP[d])		
		k = 0
		rdLen = []
		while k < len(possibleIDP):
			rdLen.append(float(possibleIDP[k+1]))
			k = k + 2
		
		#bubble sort
		#passs = 1
		#i = 0
		#while passs < countIDP:
			#while i < countIDP - passs:
				#if rdLen[i] > rdLen[i+1]:
					#temp = rdLen[i]
					#rdLen[i] = rdLen[i+1]
					#rdLen[i+1] = temp
				#i = i + 1
			#passs = passs + 1
		rdLen.sort()
		for dd in xrange(len(rdLen)):
			print str(rdLen[dd])

		m = 0
		global possibleIDPSorted
		possibleIDPSorted = []
		while m < len(rdLen):
			cur = rdLen[m]
			n = 0
			while n < len(possibleIDP):
				now = possibleIDP[n+1]
				if cur == now:
					possibleIDPSorted.append(str(possibleIDP[n]))
					possibleIDPSorted.append(str(possibleIDP[n+1]))	
				n = n + 2
			m = m + 1

		print "sorted"
		for d in xrange(len(possibleIDPSorted)):
			print str(possibleIDPSorted[d])		

		self.dlg.ui.cmbIDPCampR.clear() 
		j = 0    		
		while j < len(possibleIDPSorted):
			self.dlg.ui.cmbIDPCampR.addItem(str(possibleIDPSorted[j]))
			j = j + 2
	movieee.stop()
	self.dlg.ui.lblWait.setVisible( False )
	self.dlg.ui.btnshowDetailsIDP.setVisible(True)
	

    def	showHowDetailsIDP(self):
	global possibleIDPSorted
	global startName
	self.dlgResD.show()
	self.dlgResD.txtShowHow.clear()
	show = "Distance " + "<b>To</b>" + " non-affected IDP Camps " + "<b>From</b> " + str(startName) 
	self.dlgResD.txtShowHow.setText(str(show))
	colHeads = '<table style="width:300px"><tr><th width="200" align="left">IDP Camp</th><th></th><th width="200" align="left">Distance(~km)</th></tr>'
	self.dlgResD.txtShowHow.append('')	
	self.dlgResD.txtShowHow.append( colHeads )
	j = 0    		
	while j < len(possibleIDPSorted):
		values = '<tr><td width="200">' + str(possibleIDPSorted[j]) + '</td><td></td><td width="200">' + str(round(float(possibleIDPSorted[j+1]),2)) + '</td><td></td></tr>'
		self.dlgResD.txtShowHow.append( values )
		j = j + 2


    def getFieldName(self, layer):
		try:
			fields = layer.pendingFields()
			fCount = fields.count()
			d = 0
			fieldName = ''
			while d < fCount:
				colHead = str(fields.field(d).name())
				colHeadLower = colHead.lower()
				for c in string.punctuation:
					colHeadLower= colHeadLower.replace(c," ")
				term = "name"
				words = colHeadLower.split()
				if term in words:
					fieldName = colHead
				d = d + 1
			if fieldName == '':
				fieldName = str(fields.field(0).name())
			return fieldName
		except:
			e = sys.exc_info()[0]
			print e

    def getFieldRoadType(self, layer):
		try:
			fields = layer.pendingFields()
			fCount = fields.count()
			d = 0
			fieldName = ''
			while d < fCount:
				colHead = str(fields.field(d).name())
				colHeadLower = colHead.lower()
				for c in string.punctuation:
					colHeadLower= colHeadLower.replace(c," ")
				term = "type"
				words = colHeadLower.split()
				if term in words:
					fieldName = colHead
				d = d + 1
			if fieldName == '':
				fieldName = str(fields.field(1).name())
			return fieldName
		except:
			e = sys.exc_info()[0]
			print e

    def getFieldRoadRef(self, layer):
		try:
			fields = layer.pendingFields()
			fCount = fields.count()
			d = 0
			fieldName = ''
			while d < fCount:
				colHead = str(fields.field(d).name())
				colHeadLower = colHead.lower()
				for c in string.punctuation:
					colHeadLower= colHeadLower.replace(c," ")
				term = "ref"
				words = colHeadLower.split()
				if term in words:
					fieldName = colHead
				d = d + 1
			if fieldName == '':
				fieldName = str(fields.field(2).name())
			return fieldName
		except:
			e = sys.exc_info()[0]
			print e

    def getFieldRoadOneway(self, layer):
		try:
			fields = layer.pendingFields()
			fCount = fields.count()
			d = 0
			fieldName = ''
			while d < fCount:
				colHead = str(fields.field(d).name())
				colHeadLower = colHead.lower()
				for c in string.punctuation:
					colHeadLower= colHeadLower.replace(c," ")
				term = "oneway"
				words = colHeadLower.split()
				if term in words:
					fieldName = colHead
				d = d + 1
			if fieldName == '':
				fieldName = str(fields.field(3).name())
			return fieldName
		except:
			e = sys.exc_info()[0]
			print e

    def getFieldRoadBridge(self, layer):
		try:
			fields = layer.pendingFields()
			fCount = fields.count()
			d = 0
			fieldName = ''
			while d < fCount:
				colHead = str(fields.field(d).name())
				colHeadLower = colHead.lower()
				for c in string.punctuation:
					colHeadLower= colHeadLower.replace(c," ")
				term = "bridge"
				words = colHeadLower.split()
				if term in words:
					fieldName = colHead
				d = d + 1
			if fieldName == '':
				fieldName = str(fields.field(4).name())
			return fieldName
		except:
			e = sys.exc_info()[0]
			print e

    def getFieldRoadTunnel(self, layer):
		try:
			fields = layer.pendingFields()
			fCount = fields.count()
			d = 0
			fieldName = ''
			while d < fCount:
				colHead = str(fields.field(d).name())
				colHeadLower = colHead.lower()
				for c in string.punctuation:
					colHeadLower= colHeadLower.replace(c," ")
				term = "tunnel"
				words = colHeadLower.split()
				if term in words:
					fieldName = colHead
				d = d + 1
			if fieldName == '':
				fieldName = str(fields.field(5).name())
			return fieldName
		except:
			e = sys.exc_info()[0]
			print e




    def stopHospLocIndexChanged(self):
		try:
			global stopHospLayer
			#global rH
			HospSelected = self.dlg.ui.cmbHospitalR.currentText()							
			for feature in stopHospLayer.getFeatures():
				#g = QgsGeometry()
				global fieldNameHosp						
				col = feature[fieldNameHosp]
				#print fieldNameIDP
				geom = feature.geometry()
				if HospSelected != 'Select Hospital': #and rH == 0:
					if col == HospSelected: 
						fid=feature.id()
						#self.cLayer.select(fid)
						pointStopHosp = geom.asPoint()
						print pointStopHosp
						print float(str(pointStopHosp.x()))
						print float(str(pointStopHosp.y()))
						#feature.color
						#global mm
		       				#mm = QgsVertexMarker(self.canvas)
						# x=float(str(point.x()))
						# y=float(str(point.y()))
		       				#mm.setCenter(pointStopIDP)
		       				#mm.setColor(QColor(0,255,0))
		       				#mm.setIconSize(6)
                       				#mm.setIconType(QgsVertexMarker.ICON_BOX) # ICON_CROSS, ICON_X
                       				#mm.setPenWidth(4)
						##update stop text browsers
	        				self.dlg.clearTextBrowserStop()
        					self.dlg.setTextBrowserStop( "<b>X</b> : "+str(pointStopHosp.x()) + " , <b>Y</b> : " +str(pointStopHosp.y()) )
						self.dlg.ui.lblWarnRoad.setVisible(True)
						global x2
						global y2		
						x2=float(str(pointStopHosp.x()))
						y2=float(str(pointStopHosp.y()))		
						self.markStop()
						self.dlg.clearTextBrowserDesStop()
						bb = '<b>'
						bbs = '</b>'
						global stopLabel
						global stopName					
						stopName = bb + 'Location : ' + bbs + str(HospSelected)
						stopLabel = str(HospSelected)
						global stopNameForReport
						stopNameForReport = "<b>Location</b> : " + str(HospSelected)
						self.dlg.setTextBrowserDesStop(str(stopName))

		except:
			e = sys.exc_info()[0]
			print e


    def stopIDPLocIndexChanged(self):
		try:
			global stopIDPLayer
			#global rI
			IDPSelected = self.dlg.ui.cmbIDPCampR.currentText()							
			for feature in stopIDPLayer.getFeatures():
				#g = QgsGeometry()
				global fieldNameIDP						
				col = feature[fieldNameIDP]
				#print fieldNameIDP
				geom = feature.geometry()
				if IDPSelected != 'Select IDP Camp': #and rI == 0:
					if col == IDPSelected: 
						fid=feature.id()
						#self.cLayer.select(fid)
						pointStopIDP = geom.asPoint()
						print pointStopIDP
						print float(str(pointStopIDP.x()))
						print float(str(pointStopIDP.y()))
						#feature.color
						#global mm
		       				#mm = QgsVertexMarker(self.canvas)
						# x=float(str(point.x()))
						# y=float(str(point.y()))
		       				#mm.setCenter(pointStopIDP)
		       				#mm.setColor(QColor(0,255,0))
		       				#mm.setIconSize(6)
                       				#mm.setIconType(QgsVertexMarker.ICON_BOX) # ICON_CROSS, ICON_X
                       				#mm.setPenWidth(4)
						##update stop text browsers
	        				self.dlg.clearTextBrowserStop()
        					self.dlg.setTextBrowserStop( "<b>X</b> : "+str(pointStopIDP.x()) + " , <b>Y</b> : " +str(pointStopIDP.y()) )
						self.dlg.ui.lblWarnRoad.setVisible(True)
						global x2
						global y2		
						x2=float(str(pointStopIDP.x()))
						y2=float(str(pointStopIDP.y()))		
						self.markStop()
						self.dlg.clearTextBrowserDesStop()
						bb = '<b>'
						bbs = '</b>'
						global stopLabel
						global stopName					
						stopName = bb + 'Location : ' + bbs + str(IDPSelected)
						stopLabel = str(IDPSelected)
						global stopNameForReport
						stopNameForReport = "<b>Location</b> : " + str(IDPSelected)
						self.dlg.setTextBrowserDesStop(str(stopName))
		except:
			e = sys.exc_info()[0]
			print e
						

    #def addLabel(self):
	#self.labelPos.setVisible(False)
	#global cur
	#global plce
	#self.labelPos = QtGui.QLabel(self.canvas)
        #self.labelPos.setGeometry(QtCore.QRect(cur.x(),cur.y(), 150, 25))
        #font = QtGui.QFont()
        #font.setPointSize(16)
        #font.setBold(True)
        #font.setWeight(75)
        #self.labelPos.setFont(font)
        # self.labelPos.setObjectName(_fromUtf8("lblPos"))
	#self.labelPos.setText(str(plce))
	#self.labelPos.setVisible(True)
	#self.cursor = QCursor()
	#cursor = self.textCursor()
	#self.cursor.setToolTip("cursor")
	#posi = self.cursor.pos()
	#print str(posi)


    def clickedCanvas(self):
	global stopPlace
	stopPlace = 0
	global stopPlaceDir
	stopPlaceDir = 0
	#global curX
	#global curY
	#self.labelPos.setGeometry(QtCore.QRect(curX ,curY, 150, 25))		
	#curX = 100
	#curY = 100
	print "clicked"
	#self.labelPos.setText("<i><b>Click again to confirm</b></i>")
	#global stopNow
	#stopNow = 0
	#global stopPlace
	#stopPlace = 0
	#global okNow
	#okNow = 2

    def cursorMove(self, point):
	print "come"
	#QObject.connect(self.curMove, SIGNAL("xyCoordinates( const QgsPoint &p	))"), self.cursorMove)
	#mCanvasProperties.mouseLastXY = e.pos()
	#if ( mCanvasProperties.panSelectorDown ):
	#	panAction( e )
	#else:
	#	if ( mMapTool ):
	#		mMapTool.canvasMoveEvent( e );
	#xy = e.pos();
	#QPoint(xy)
	#coord = getCoordinateTransform().toMapCoordinates( xy )
	#QgsPoint(coord)	
	#return xyCoordinates( coord )
	#print str(point)
    #no need	
    def pointCursor(self):
	#self.labelPos.setVisible(True)
	global stopNow
	#global stopPlace
	if stopNow == 1:
		#print val
		#self.labelPos.setVisible(True)
		global cur
		global plce
		#posi = self.cursor.pos()
		cur = self.iface.mapCanvas().mouseLastXY()		
		myMapToPixel = self.iface.mapCanvas().getCoordinateTransform()
		#QPoint(cur)
		xy = myMapToPixel.toMapCoordinates(cur)
		#self.addLabel()
		#print xy
		pointt = QgsPoint(xy)
		plce = self.getPlaceDir(pointt)
		print plce
		#self.addLabel()
		#self.labelPos = QtGui.QLabel(self.canvas)
        	# self.labelPos.setObjectName(_fromUtf8("lblPos"))
		#global stopPlace
		#if stopPlace == 1:
			#self.labelPos.setText(str(plce))
			#self.labelPos.setVisible(True)	
		#self.labelPos.setVisible(True)
		#self.place()
		self.pointCursor()
		#self.labelPos.setVisible(True)
		#global val
		#val = 2
		#self.selectStart()
	#elif val == 2:
		#print val
		#cur = self.iface.mapCanvas().mouseLastXY()
		#myMapToPixel = self.iface.mapCanvas().getCoordinateTransform()
		#QPoint(cur)
		#xy = myMapToPixel.toMapCoordinates(cur)
		#print xy
		#pointt = QgsPoint(xy)
		#plce = self.getPlaceDir(pointt)
		#print plce
		#self.selectStart()
	#else:
		#print "finish"
		#global resultCon
		#global okNow
		#okNow = 2
		#self.selectStart()
    #no need above		
    def place(self):
		sizeOp = '<h2>'
		sizeCl = '<\h2>'
		#self.labelPos.setVisible(False)
		global stopPlace
		#self.clickTool.canvasClicked.connect(self.clickedCanvas)
		while stopPlace == 1:
			try:		
				global stopPlace
				#self.labelPos.setText(str(plce))
				#global plce
				#global cur
				#self.labelPos.clear()
				cur = self.iface.mapCanvas().mouseLastXY()
				#global curX
				#global curY	 
				curX = cur.x()
				curY = cur.y()
				self.labelPos.setGeometry(QtCore.QRect(0 ,0, 600, 100))		
				myMapToPixel = self.iface.mapCanvas().getCoordinateTransform()
				#QPoint(cur)
				xy = myMapToPixel.toMapCoordinates(cur)
				#self.addLabel()
				#print xy
				pointt = QgsPoint(xy)
				plce = self.getPlaceDirName(pointt)
				#sizeOp = '<h2>'
				#sizeCl = '<\h2>'
				plceName = sizeOp + "<b>Location :</b> " + str(plce) + sizeCl
				print plceName
				#self.dlg.setTextBrowserDesStart(str(plceName))
				#lp = plceName
				#lp = 0			
				#while lp < 5000:
					#lp = lp + 1
		        	#self.labelPos.setGeometry(QtCore.QRect(cur.x(),cur.y(), 150, 25))
        			#font = QtGui.QFont()
        			#font.setPointSize(16)
        			#font.setBold(True)
        			#font.setWeight(75)
        			#self.labelPos.setFont(font)
				self.labelPos.setVisible(True)
				#self.labelPos.clear()	
				self.labelPos.setText(str(plceName))
				#self.labelPos.setVisible(False)			
				#self.pointCursor()
				#self.clickTool.canvasClicked.connect(self.clickedCanvas)
				#self.place()
			except:
				e = sys.exc_info()[0]
				print e
				#self.place()
		else:
			self.labelPos.clear()
			fin = sizeOp + "<i><b>Click again to confirm</b></i>" + sizeCl
			self.labelPos.setText(str(fin))	

    def getPlaceDetails(self, point):
		# setup the provider select to filter results based on a rectangle
       		pntGeom = QgsGeometry.fromPoint(point)
       		# scale-dependent buffer of 2 pixels-worth of map units
       		pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       		rect = pntBuff.boundingBox()
       		# get currentLayer and dataProvider
       		cLayer = self.canvas.currentLayer()
		self.provider = cLayer.dataProvider()
              	request = QgsFeatureRequest().setFilterRect(rect)
		try:
 	    		feature = cLayer.getFeatures(request).next()
		#except StopIteration:
			#print "Feature not found"
			#nIndx = self.provider.fieldNameIndex('NAME')
			fields = cLayer.pendingFields()
			fCount = fields.count()
			d = 0
			columnHead = ''
			columnData = ''
			while d < fCount:
				columnHead = columnHead + str(fields.field(d).name()) + " \t "
				columnData = columnData + str(feature[d]) + " \t "
				d = d + 1			
			#if nIndx != -1:
	   			#featr = feature['NAME']
			#else:
			columnFull = columnHead + " \n " + columnData
			featr = columnFull
			return featr
		except StopIteration:
			print "Feature not found"		
 

    def travelByCar(self):
	global mode
	mode = "By Car"
	self.dlg.ui.cmbSpeedOfTravel.setCurrentIndex(2)
	#self.timeToTravel()

    def travelWalk(self):
	global mode
	mode = "Walking"
	self.dlg.ui.cmbSpeedOfTravel.setCurrentIndex(0)
	self.timeToTravel()

    def speedIndexChanged(self):
	self.timeToTravel()	

    def timeToTravel(self):
	global hrs
	global minutes
	global dKmH
	dKmH = float(self.dlg.ui.cmbSpeedOfTravel.currentText())
	dMilesH = dKmH * 0.621371
	self.dlg.ui.txtSpeedMph.clear()
	self.dlg.ui.txtSpeedMph.setText(str(dMilesH))
	#time
	global ds
	time = ds / dKmH
	timeRound = round(time, 2)
	print timeRound
	hrs = int(timeRound)
	number_dec = str(timeRound-int(timeRound))[1:]
	#print number_dec
	mins = float(number_dec) * 60
	minutes = int(mins)
	print hrs
	print mins
	print int(mins)
	global nowHrs
	global nowMins
	nowHrs = hrs
	nowMins = minutes
	self.dlg.ui.txtTimeToTravelHrs.clear()
	self.dlg.ui.txtTimeToTravelMins.clear()
	self.dlg.ui.txtTimeToTravelHrs.setText(str(hrs))
	self.dlg.ui.txtTimeToTravelMins.setText(str(minutes))
		

    #A*
    def make_graph(self, mapinfo):
    	nodes = [[AStarGridNode(x, y) for y in range(mapinfo['height'])] for x in range(mapinfo['width'])]
    	graphAstar = {}
    	for x, y in product(range(mapinfo['width']), range(mapinfo['height'])):
		#print x
		#print y        	
		node = nodes[x][y]
        	graphAstar[node] = []
        	for i, j in product([-1, 0, 1], [-1, 0, 1]):
            		if not (0 <= x + i < mapinfo['width']): continue
            		if not (0 <= y + j < mapinfo['height']): continue
            		graphAstar[nodes[x][y]].append(nodes[x+i][y+j])
    	return graphAstar, nodes, point1, point2

    #A*

    def findRoutes(self):
	# QMessageBox.information( self.iface.mainWindow(),"Info", "in findRoutes function" )
	# vl = qgis.utils.iface.mapCanvas().currentLayer()
	self.dlg.ui.lblWarnRoad.setVisible(False)
	vl=self.canvas.currentLayer()
	director = QgsLineVectorLayerDirector( vl, -1, '', '', '', 3 )
	properter = QgsDistanceArcProperter()
	director.addProperter( properter )
	# crs = qgis.utils.iface.mapCanvas().mapRenderer().destinationCrs()
	crs = self.canvas.mapRenderer().destinationCrs()
	builder = QgsGraphBuilder( crs )
	
	global x1
	global y1
	global x2
	global y2
	pStart = QgsPoint( x1, y1 )
	pStop = QgsPoint( x2, y2 )
	
	tiedPoints = director.makeGraph( builder, [ pStart, pStop ] )
	#tiedPoints = director.makeGraph( builder, [ pStart ] )
	graph = builder.graph()
	tStart = tiedPoints[ 0 ]
	tStop = tiedPoints[ 1 ]
	idStart = graph.findVertex( tStart )
	idStop = graph.findVertex( tStop )
	( tree, cost ) = QgsGraphAnalyzer.dijkstra( graph, idStart, 0 )

	# QMessageBox.information( self.iface.mainWindow(),"Cost", str(len(cost)) )

	if tree[ idStop ] == -1:
		#print "Path not found"
		#self.clearFields()
		self.dlg.clearTextBrowserStop()
		self.dlg.clearTextBrowserDesStop()
		try:
			global m2
			self.canvas.scene().removeItem(m2)
			self.dlg.ui.lblWarnRoad.setVisible(False)
			global stopPlace
			stopPlace == 1
			self.labelPos.clear()
		except:
			e = sys.exc_info()[0]
		QMessageBox.information( self.iface.mainWindow(),"Sorry", "No path found between selected locations" )
	else:
		global p
		p = []
		curPos = idStop
		
		while curPos != idStart:
			p.append( graph.vertex( graph.arc( tree[ curPos ] ).inVertex() ).point() )
			curPos = graph.arc( tree[ curPos ] ).outVertex();
		
		p.append( tStart )
		#p.append( tStop )
		
		#rb = QgsRubberBand( qgis.utils.iface.mapCanvas() )
		global rb		
		rb = QgsRubberBand( self.canvas )
		rb.setColor( Qt.red )
		rb.setWidth(4)

		global pcount
		global pcountLbl
		global pointsForImage
		pointsForImage = []		
		pcount = 0
		pcountLbl = 0		
		for pnt in p:
			rb.addPoint(pnt)
			print pnt
			pointsForImage.append(pnt)
			#test
			#global mm
			#mm = QgsVertexMarker(self.canvas)
			#mm.setCenter(QgsPoint(pnt))
			#mm.setColor(QColor(0,0,255))
			#mm.setIconSize(3)
        		#mm.setIconType(QgsVertexMarker.ICON_X) # ICON_CROSS, ICON_X
        		#mm.setPenWidth(3)
			#test above
			pl = self.getPlaceDirName(QgsPoint(pnt))
			#print str(pl)
			#myMapToPixell = self.iface.mapCanvas().getCoordinateTransform()
			#xyy = myMapToPixell.toMapCoordinates(pnt)
			labelDirPlc = "lbl" + str(pcount)
			self.labelDirPlc = QtGui.QLabel(self.canvas)
			#p1 = xyy.x()
			#p2 = xyy.y()
			pp = QPoint(pnt.x(),pnt.y())
			print str(pp)
			#self.labelDirPlc.setGeometry(QtCore.QRect(pp.x(),pp.y(), 200, 100))
        		font = QtGui.QFont()
        		font.setPointSize(5)
        		font.setWeight(20)
        		self.labelDirPlc.setFont(font)
			self.labelDirPlc.setText(str(pl))
			#self.labelDirPlc.setVisible(True)
			#test code above
			pcount = pcount +1
			pcountLbl = pcountLbl + 1
	
		print pcount
		print "now"
		#self.labell()
		#self.labell()
		print "out"

		self.fillDirecDetails()

		global startLabel
		global stopLabel
		global vl
		global tempLayer
		tempLayer = "temporary_points"
		# create layer
		vl = QgsVectorLayer("Point?crs=epsg:4326", "temporary_points", "memory")
		pr = vl.dataProvider()
		# add fields
		vl.startEditing()
		pr.addAttributes( [ QgsField("name", QVariant.String) ] )
		# add a feature
		fet = QgsFeature()
		fet.setGeometry( QgsGeometry.fromPoint( pStart ))
		fet.setAttributes([str(startLabel)])
		pr.addFeatures([fet])
		fett = QgsFeature()
		fett.setGeometry( QgsGeometry.fromPoint( pStop ))
		fett.setAttributes([str(stopLabel)])
		pr.addFeatures([fett])

		# update layer’s extent when new features have been added
		# because change of extent in provider is not propagated to the layer
		vl.updateExtents()
		vl.commitChanges()
		#verify layer craeted
		print "fields:", len(pr.fields())
		print "features:", pr.featureCount()
		f = QgsFeature()
		features = vl.getFeatures()
		for f in features:
			print "F:",f.id(), f.attributes(), f.geometry().asPoint()
		QgsMapLayerRegistry.instance().addMapLayer(vl)

		self.hideLabellingFeatures()
		palyr = QgsPalLayerSettings()
		palyr.readFromLayer(vl)
		palyr.enabled = True
		palyr.fieldName = 'name'
		palyr.placement = QgsPalLayerSettings.OverPoint
		palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'10','')
		#palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'color.red','')
		palyr.writeToLayer(vl)
		self.canvas.refresh()

		#change color
		symbols = vl.rendererV2().symbols()
		symbol = symbols[0]
		symbol.setColor(QtGui.QColor.fromRgb(0,0,255))
		self.canvas.refresh() 
		self.iface.legendInterface().refreshLayerSymbology(vl)
		#QObject.connect(self.curMove, SIGNAL("xyCoordinates( const QgsPoint &p	))"), self.cursorMove)
		#self.getdirections()
		#print p[pcount-1]
		#i = 0
		#lastIndex = pcount-1
#		angle = []
#		dist = []
#		angCount = 0
#		while pcount > 1 :
#			point1 = QgsPoint(p[pcount-1])
#			print p[pcount-1]			
#			point2 = QgsPoint(p[pcount-2])
#			print p[pcount-2]
#			angle.append(int(self.getAngle(point1, point2)))
#			dist.append(self.distance(point1.x(), point1.y(), point2.x(), point2.y()))
#			var = int(self.getAngle(point1, point2))
#			print var
#			var2 = self.distance(point1.x(), point1.y(), point2.x(), point2.y())
#			print var2
#			angCount = angCount + 1
			#if angle > 0 and angle < 90:
				#corAngle = 90 - angle
			#elif angle >=90 and angle < 180:
				#corAngle = 180 - angle
			#elif angle < 0 and angle > -90:
				#corAngle = 90 + angle			
			#elif angle <= -90 and angle > -180:
				#corAngle = 180 + angle			
			#else:
				#corAngle = angle
			#print corAngle	
#			pcount = pcount-1

		#for ang in angle:
#		i = 0
#		j = 1
		#print angCount
#		dirAngle = 0
#		direc = 'go Straight'
#		length = dist[0]
#		print "angle : " + str(dirAngle) + " direction : " + str(direc) + " distance : " + str(length) + " km"		
#		while i < (angCount-1):			
#			p1 = angle[i]
#			p2 = angle[i + 1]
			#if (p1 > 0 and p2 > 0) or (p1 < 0 and p2 < 0):
#			if p2 > p1:
#				if ((p1 < -90 and p1 > -180) and (p2 > 90 and p2 < 180)):
#					dirAngle = (180 + p1) + (180 - p2)
#					direc = 'turn Left'
#				else:
#					dirAngle = p2 - p1
#					direc = 'turn Right'
#			elif p2 < p1:
#				if ((p1 > 90 and p1 < 180) and (p2 < -90 and p2 > -180)):
#					dirAngle = (180 - p1) + (180 + p2)
#					direc = 'turn Right'
#				else:
#					dirAngle = p1 - p2
#					direc = 'turn Left'
#			else:
#				dirAngle = 0
#				direc = 'go Straight'
#			length = dist[j]
#			j = j + 1	
#			print str(p1) + " and " + str(p2)						
#			print "angle : " + str(dirAngle) + " direction : " + str(direc) + " distance : " + str(length) + " km"	
#			i = i + 1


#getAngle
#distance(self, lon1, lat1, lon2, lat2):
	##extraa
	#for edgeId in tree:
		#if edgeId == -1:
			#continue
		#rbEx = QgsRubberBand( self.canvas )
		#rbEx.setColor ( Qt.green )
		#rbEx.addPoint ( graph.vertex( graph.arc( edgeId ).inVertex() ).point() )
		#rbEx.addPoint ( graph.vertex( graph.arc( edgeId ).outVertex() ).point() )
	#rbEx.addPoint( tStart )	
	
	##extraa

	#networkx

	#lyr_1 = nx.read_shp(str(iface.activeLayer().source()))
	G = nx.read_shp(str(self.canvas.currentLayer().source()))
	G.add_node((x1, y1))
	G.add_node((x2, y2))
	##G.add_edge((x1, y1), (x2, y2))

	i=0
	#nodeStartIndex = 0
	#nodeStopIndex = 0
	#print G.number_of_nodes()
	#while i < G.number_of_nodes():		
	for node in G.nodes():
		if node == (( x1, y1 )):
			nodeStartIndex = i
		elif node == ((x2, y2)):
			nodeStopIndex = i
		i = i+1

	#print i
	#global nodeStartIndex
	#global nodeStopIndex 
	#print nodeStartIndex
	#print nodeStopIndex

	startNode = G.nodes()[nodeStartIndex]
	endNode = G.nodes()[nodeStopIndex]

	#networkx




	#new_dijkstra
	#tree = self.dijk.shortest_path( G, startNode, endNode )
	#if tree is None:
    		#print "No path found"
		#QMessageBox.information( self.iface.mainWindow(),"Info", "No path found" )
	#else:
   	 	#print "Path found:"#, path
		#QMessageBox.information( self.iface.mainWindow(),"Info", "Path found" )

	
	#new_dijkstra
	
	#extra 
	
	#for edgeId in tree:
		#if edgeId == -1:
			#continue
		#global rbb		
		#rbb = QgsRubberBand( self.canvas )
		#rbb.setColor ( Qt.green )
		#rbb.setWidth(4)
		#rbb.addPoint ( graph.vertex( graph.arc( edgeId ).inVertex() ).point() )
		#rbb.addPoint ( graph.vertex( graph.arc( edgeId ).outVertex() ).point() )


	#extra
	
		
	#new
		# QMessageBox.information( self.iface.mainWindow(),"Cost", str(len(cost)) )		
		#upperBound = []
		#r = 10000.0
		#i = 0
		#while i < len(cost):
			# QMessageBox.information( self.iface.mainWindow(),"Info", str(cost[ i ]) )
			#if cost[ i ] > r and tree[ i ] != -1:
				#outVertexId = graph.arc( tree [ i ] ).outVertex()
				# QMessageBox.information( self.iface.mainWindow(),"Cost_out", str(cost[ outVertexId ]) )				
				#if cost[ outVertexId ] < r:
					#upperBound.append( i )
					# QMessageBox.information( self.iface.mainWindow(),"Info", "in findRoutes function" )
			#i = i + 1	


		# QMessageBox.information( self.iface.mainWindow(),"Info", str( i ) )		
		#for edgeId in upperBound:
#	for edgeId in tree:
			#if edgeId == -1:
				#continue
			#global rb
			#rb = QgsRubberBand( self.canvas )
			#rb.setColor ( Qt.green )
			#rb.setWidth(4)
			#rb.addPoint ( graph.vertex( graph.arc( edgeId ).inVertex() ).point() )
			#rb.addPoint ( graph.vertex( graph.arc( edgeId ).outVertex() ).point() )
			#QMessageBox.information( self.iface.mainWindow(),"Info", str( edgeId ) )

		#for i in upperBound:
			#centerPoint =( graph.arc( i ).inVertex() ).point()
			#global rb
			#rb = QgsRubberBand( self.canvas, True )
			#rb.setColor ( Qt.green )
			#rb.setWidth(4)
			#QMessageBox.information( self.iface.mainWindow(),"Info", "in" )
			#rb.addPoint( graph.vertex( graph.arc( tree[ i ] ).inVertex() ).point() )
			#rb.addPoint( graph.vertex( graph.arc( tree[ i ] ).outVertex() ).point() )
			#i = i + 1

	#A*
	
    #def make_graph(mapinfo):
    	#nodes = [[AStarGridNode(x, y) for y in range(mapinfo.height)] for x in range(mapinfo.width)]
    	#graph = {}
    	#for x, y in product(range(mapinfo.width), range(mapinfo.height)):
        	#node = nodes[x][y]
        	#graph[node] = []
        	#for i, j in product([-1, 0, 1], [-1, 0, 1]):
            		#if not (0 <= x + i < mapinfo.width): continue
            		#if not (0 <= y + j < mapinfo.height): continue
            		#graph[nodes[x][y]].append(nodes[x+i][y+j])
			#QMessageBox.information( self.iface.mainWindow(),"Info", "come5" )
    	#return graph, nodes

    #def my_graph(self, mapinfo):	
	#global x1
	#global y1
	#global x2
	#global y2
	#start = [[AStarGridNode(x1, y1)]]	
	#end = [[AStarGridNode(x2, y2)]]
	#print nodesz    	
	#nodes = [[AStarGridNode(x2, y2) for y2 in range(mapinfo['height'])] for x2 in range(mapinfo['width'])]

	##	graphAstar, nodes = self.make_graph({ "width": 8, "height": 8 })
	#print point1
	#print point2
	#print nodes[0][0]
	#print nodes[0][1]
	#paths = AStarGrid(G)
	##	paths = AStarGrid(graphAstar)
	
	#tiedPoints = director.makeGraph( builder, [ pStart, pStop ] )
	#tStart = tiedPoints[ 0 ]
	#tStop = tiedPoints[ 1 ]	
	#graphAstar.add_node([pStart])
	#graphAstar.add_node([pStop])	
	
	#print nodes[1][1]
	#print nodes[5][7]	
	#start, end = nodes[0][0], nodes[0][1]
	#start = (x1, y1)
	#end = (x2, y2)
	#path = self.astar.astarSearch(G, startNode, endNode)
	##    path = self.astar.astarSearch(graph, idStart, idStop)
	#path = paths.astarSearch(start, end)
	#start = AStarGridNode(x1, y1)
	#end = AStarGridNode(x2, y2)
	#print start
	#print end
	#start = graphAstar.add_node(pStart)
	#end = graphAstar.add_node(pStop)
	## path = paths.search(start, end)
	#QMessageBox.information( self.iface.mainWindow(),"Info", "come1" )
	#if path is None:
    		# print "No path found"
		#QMessageBox.information( self.iface.mainWindow(),"Info", "No path found" )
	#else:
   	 	# print "Path found:", path
		#QMessageBox.information( self.iface.mainWindow(),"Info", "Path found" )

	#aStar(graph, idStart, idStop)

	#edited

	#x=0
	#y=0	
	#for node in nodes:
	#	if node[x]		


	
	##	start, end = (x1, y1), (x2, y2)
	#start[0]
	##print end
	#print nodes[start[0]][start[1]]
	#print nodes[end[0]][end[1]]
	#path = paths.search(nodes[start[0]][start[1]], nodes[end[0]][end[1]]) 
	#path = paths.search(start, end) 

	#edited


	#A*

	#A*-networkx

	#path = self.astarnetx.astar_path(G,(x1, y1),(x1, y1))

	#path = nx.astar_path(G,start,end,None)	
	
	#A*-networkx

	

	#new2_astar
	#start, end = idStart, idStop
	#path=self.astarnetx.astar_path(G, startNode, endNode)
	#path=self.astar.astarSearch(G, startNode, endNode)
	#if path is None:
    		#print "No path found"
		##QMessageBox.information( self.iface.mainWindow(),"Info", "No path found" )
	#else:
   	 	#print "Path found:", path
		##QMessageBox.information( self.iface.mainWindow(),"Info", "Path found " )
		#for i in path:		
			#QMessageBox.information( self.iface.mainWindow(),"Info", path[i] )

	#new2_astar	



	#new

	#delta = self.canvas.getCoordinateTransform().mapUnitsPerPixel() * 1
	#global rb	
	#rb = QgsRubberBand( self.canvas, True )
	#rb.setColor( Qt.green )
	#rb.addPoint( QgsPoint( pStart.x() - delta, pStart.y() - delta ) )
	#rb.addPoint( QgsPoint( pStart.x() + delta, pStart.y() - delta ) )
	#rb.addPoint( QgsPoint( pStart.x() + delta, pStart.y() + delta ) )
	#rb.addPoint( QgsPoint( pStart.x() - delta, pStart.y() + delta ) )

	#tiedPoints = director.makeGraph( builder, [ pStart ] )
	#graph = builder.graph()
	#tStart = tiedPoints[ 0 ]
	#idStart = graph.findVertex( tStart )
	#( tree, cost ) = QgsGraphAnalyzer.dijkstra( graph, idStart, 0 )
	#upperBound = []
	#r = 2000.0
	#i = 0
	#while i < len(cost):
		#if cost[ i ] > r and tree[ i ] != -1:
			#outVertexId = graph.arc( tree [ i ] ).outVertex()
			#if cost[ outVertexId ] < r:
				#upperBound.append( i )
		#i = i + 1	

	#for i in upperBound:
		#centerPoint = graph.vertex( i ).point()
		#global rb
		#rb = QgsRubberBand( self.canvas, True )
		#rb.setColor( Qt.red )
		#rb.addPoint( QgsPoint( centerPoint.x() - delta, centerPoint.y() - delta ) )
		#rb.addPoint( QgsPoint( centerPoint.x() + delta, centerPoint.y() - delta ) )
		#rb.addPoint( QgsPoint( centerPoint.x() + delta, centerPoint.y() + delta ) )
		#rb.addPoint( QgsPoint( centerPoint.x() - delta, centerPoint.y() + delta ) )

	
	#new - ShortestTree()
	#tree = QgsGraphAnalyzer.shortestTree( graph, idStart, 0 )
	#idStart = tree.findVertex( tStart )
	#idStop = tree.findVertex( tStop )
	#if idStop == -1:
		#print "Path not found"
	#else:
		#p = []
		#while ( idStart != idStop ):
			#l = tree.vertex( idStop ).inArc()
			#if len( l ) == 0:
				#break
			#e = tree.arc( l[ 0 ] )
			#p.insert( 0, tree.vertex( e.inVertex() ).point() )
			#idStop = e.outVertex()

		#p.insert( 0, tStart )
		#global rb
		#rb = QgsRubberBand( self.canvas )
		#rb.setColor( Qt.red )
		#rb.setWidth(4)

		#for pnt in p:
			#rb.addPoint(pnt)
	#new - ShortestTree()
	#QMessageBox.information( self.iface.mainWindow(),"Info", "down" )
	#r = QgsRubberBand(self.canvas, False) # False = not a polygon
	#global x1
	#global y1
	#global x2
	#global y2	
	# points = [ QgsPoint(x1,y1), QgsPoint(x2,y2) ]
	#points = [ graph.arc( tree[ idStart ] ), graph.arc( tree[ idStop ] ) ]
	#points = [ ( tree[ idStart ] ), ( tree[ idStop ] ) ]	
	#global r
	#r.setToGeometry(QgsGeometry.fromPolyline(points), None)
	# QMessageBox.information( self.iface.mainWindow(),"Info", "down2" )
	#r.setColor(QColor(0,0,255))
	#r.setWidth(4)
	##   self.category_from_keywords()
	#layer = get_hazard_layer()
	#print layer.name()
	#processing.runandload("qgis:intersection", "/home/kasun/jakarta jalan.shp", "/home/kasun/banjir jakarta 2007 rw.shp", "/home/kasun/LayerNew.shp")
	
	#self.keywords_from_layers()
	
	#save image for later use
	self.iface.mapCanvas().saveAsImage('/home/kasun/output_canvas.png', None, 'PNG')


    def getAngle(self, point1, point2):
        #'''azimuth between 2 QGIS points ->must be adapted to 0-360°'''
	angle = math.atan2(point2.x() - point1.x(), point2.y() - point1.y())
	if angle < 0 :
		return math.degrees(angle) + 360 # between 0 and 360
	else:    	
		return math.degrees(angle)

    def distance(self, lon1, lat1, lon2, lat2):
	lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
	#haversine formula
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
	c = 2 * math.asin(math.sqrt(a))
	km = 6371 * c # 6371 Earth’s radius in km
	return km

    def getdirections(self):
		movie = QtGui.QMovie(":/plugins/floogin/loading.gif")
		self.dlg.ui.lblLoading.setVisible( True )
		self.dlg.ui.lblLoading.setMovie(movie)
		movie.start()
		angle = []
		dist = []
		global angCount 		
		angCount = 0
		global place
		place = []
		startPlc = ''
		allStraight = 1
		global pointsRoad
		pointsRoad = []
		#global placeForLabel
		#placeForLabel = []
		global what
		what = []
		global onRoad
		onRoad = []
		global disLong
		disLong = []
		global roadDis
		roadDis = []
		global roadDir
		roadDir = []
		global lngth
		global direcForReport
		#global direcForReportSimple
		global pcountLbl
		global pcount
		global p
		#QMessageBox.information( self.iface.mainWindow(),"Info", str(pcount) )
		#place.append(self.getPlaceDirName(QgsPoint(p[pcount])))
		while pcount > 1 :
			#self.dlg.ui.txtGetDirectionsRSimple.setText(str(pcount))
			point1 = QgsPoint(p[pcount-1])
			print p[pcount-1]			
			point2 = QgsPoint(p[pcount-2])
			print p[pcount-2]
			pointsRoad.append(point1)
			angle.append(int(self.getAngle(point1, point2)))
			dist.append(self.distance(point1.x(), point1.y(), point2.x(), point2.y()))
			startPlc = self.getPlaceDirNameMoreSpecific(point1)
			place.append(self.getPlaceDirNameMoreSpecific(point1)) ##point2
			#if pcount == 2:
				#place.append(self.getPlaceDirName(point2))
			var = int(self.getAngle(point1, point2))
			print var
			var2 = self.distance(point1.x(), point1.y(), point2.x(), point2.y())
			print var2
			var3 = self.getPlaceDirNameMoreSpecific(point1)
			print var3
			angCount = angCount + 1
			#if angle > 0 and angle < 90:
				#corAngle = 90 - angle
			#elif angle >=90 and angle < 180:
				#corAngle = 180 - angle
			#elif angle < 0 and angle > -90:
				#corAngle = 90 + angle			
			#elif angle <= -90 and angle > -180:
				#corAngle = 180 + angle			
			#else:
				#corAngle = angle
			#print corAngle	
			pcount = pcount-1

		#place.append(self.getPlaceDirName(QgsPoint(p[0])))
		#for ang in angle:
		i = 0
		j = 0 ##
		k = 0 ##
		#print angCount
		direcForReport = []
		#direcForReportSimple = []
		dirAngle = 0
		direc = 'go Straight'
		length = dist[0]
		plc = place[0]
		disRoundd = round(length, 2)
		disInMeters = disRoundd * 1000
		colorOpen = '<font color="blue">'
		colorClose = '</font>'
		print "turn angle : " + str(dirAngle) + " direction : " + str(direc) + " distance : " + str(length) + " km " + " in road : " + str(plc)
		##res1 ="0. <b>angle (azimuth)</b> : " + colorOpen + str(dirAngle) + colorClose + " <b>degrees</b> " +", <b>direction</b> : " + colorOpen + str(direc) + colorClose + ", <b>distance</b> : " + colorOpen + str(length) + colorClose + " <b>km (</b> ~ " + colorOpen + str(disInMeters) + colorClose + " <b>m )</b> " + ", <b>in road</b> : " + colorOpen + str(plc) + colorClose 
		res1 ="0. <b>angle (azimuth)</b> : " + colorOpen + str(dirAngle) + colorClose + " <b>degrees</b> " +", <b>direction</b> : " + colorOpen + str(direc) + colorClose + ", <b>in road</b> : " + colorOpen + str(plc) + colorClose
		res1ForPrint ="1. <b>turn angle</b> : " + colorOpen + str(dirAngle) + colorClose + " <b>degrees</b> " +", <b>direction</b> : " + colorOpen + str(direc) + colorClose + ", <b>distance</b> : " + colorOpen + str(length) + colorClose + " <b>km</b> " + ", <b>in road</b> : " + colorOpen + str(plc) + colorClose + "\n" 
		##self.dlg.ui.txtGetDirectionsR.setText(str(res1))
		##self.dlg.ui.txtGetDirectionsR.setText('')
		#movie.stop()
		#self.dlg.ui.lblLoading.setVisible( False )
		direcForReport.append(str(res1ForPrint))
		self.dlg.ui.txtGetDirectionsRSimple.clear()
		self.dlg.ui.txtGetDirectionsRSimple.setText('')
		#global simpleCount		
		#simpleCount = 0
		#global passs
		#passs = "no"
		sameRoad = 3		
		while i < (angCount-1):##			
			p1 = angle[i]
			#try:
				#p2 = angle[i + 2]##
				#print "here2"
			#except:
			p2 = angle[i + 1]
				#print "here1"
			##newly added
			delta = p2 - p1
			print delta 
			if delta < 0:
				delta = delta + 360 #make sure angle is [0..360]
			
    			if delta > 180:
        			direc = 'turn Left'
    			elif delta < 180:
				direc = 'turn Right'
			else:
				direc = 'go Straight'

			dirAngle = p1
			if dirAngle < 0:
				dirAngle = dirAngle + 180
			##newly added above
			#if p2 > p1:
				#if ((p1 < -90 and p1 > -180) and (p2 > 90 and p2 < 180)):
					#dirAngle = (180 + p1) + (180 - p2)
					#direc = 'turn Left'
				#else:
					#dirAngle = p2 - p1
					#direc = 'turn Right'
			#elif p2 < p1:
				#if ((p1 > 90 and p1 < 180) and (p2 < -90 and p2 > -180)):
					#dirAngle = (180 - p1) + (180 + p2)
					#direc = 'turn Right'
				#else:
					#dirAngle = p1 - p2
					#direc = 'turn Left'
			#else:
				#dirAngle = 0
				#direc = 'go Straight'
			length = dist[j]
			#totLen = totLen + length
			disRounddd = round(length, 2)
			disInMeterss = disRounddd * 1000
			j = j + 1
			try:			
				plc = place[k+2]
			except:
				plc = place[k]
			k = k + 1
			newL = '<\n>'	
			print str(p1) + " and " + str(p2)						
			print "turn angle : " + str(dirAngle) + " direction : " + str(direc) + " distance : " + str(length) + " km " + " in road : " + str(plc)
			res2 = str(j) + ". " "<b>angle (azimuth)</b> : " + colorOpen + str(dirAngle) + colorClose + " <b>degrees</b> " + ", <b>direction</b> : " + colorOpen + str(direc) + colorClose + ", <b>distance</b> : " + colorOpen + str(length) + colorClose + " <b>km (</b> ~ " + colorOpen + str(disInMeterss) + colorClose + " <b>m )</b> " + ", <b>on </b> : " + colorOpen + str(plc) + colorClose	
			res2ForPrint ="\n" + str(j) + ". " "<b>angle (azimuth)</b> : " + colorOpen + str(dirAngle) + colorClose + " <b>degrees</b> " + ", <b>direction</b> : " + colorOpen + str(direc) + colorClose + ", <b>distance</b> : " + colorOpen + str(length) + colorClose + " <b>km</b> " + ", <b>in road</b> : " + colorOpen + str(plc) + colorClose + newL	

			#if dirAngle > 25: # eliminate false directions			
			##self.dlg.ui.txtGetDirectionsR.append("\n")	
			##self.dlg.ui.txtGetDirectionsR.append(str(res2))
			direcForReport.append(str(res2ForPrint))
			roadDir.append(str(plc))
			roadDir.append(str(direc))
			# Simplified directions			
			if startPlc != '':
				if startPlc == place[i]: 
					road = place[i]
					#continuer = 'yes'
					lngth = 0.0
					lngth = dist[0]
					startPlc = ''
				else: #unedited
					road = place[i]
					#continuer = 'no'
					lngth = dist[0]
					todo = colorOpen + str(direc) + colorClose +' <b>and continue on road</b> ' + colorOpen + str(road) + colorClose + " , <b>distance</b> : " + colorOpen + str(lngth) + colorClose + " <b>km</b> "
					startPlc = ''

			if place[i] == place[i+1]:
				#road = place[i+1]
				road = place[i]
				#lngth = dist[i+1]
				#if str(continuer) == 'yes':
					#global lngth
				lngth = lngth + dist[i+1]
				if i == angCount-2: # for last record
					disRound = round(lngth, 2)
					todo = '<b>Continue on</b> ' + colorOpen + str(road) + colorClose + " , <b>distance</b> : " + colorOpen + str(disRound) + colorClose + " <b>km</b> "
					roadDis.append(str(road))
					roadDis.append(disRound)
					#self.dlg.ui.txtGetDirectionsRSimple.append(str(todo))
					#direcForReportSimple.append(str(todo))
					#simpleCount = simpleCount + 1
					#todo = 'Continue on road ' + str(road)
			else:
				if 1 > 0: # false if (no need)
					#global passs
					print "comee"
					global lngth
					#allStraight = 0
					disRound = round(lngth, 2)
					todo = '<b>Continue on</b> ' + colorOpen + str(road) + colorClose + " , <b>distance</b> : " + colorOpen + str(disRound) +  colorClose + " <b>km</b> \n"
					wat = 'Continue on'
					what.append(str(wat))
					onRoad.append(str(road))
					disLong.append(str(disRound))
					roadDis.append(str(road))
					roadDis.append(disRound)
					#placeForLabel.append(str(road))					
					#if str(passs) != "yes":
					#if sameRoad > 2:
					#self.dlg.ui.txtGetDirectionsRSimple.append(str(todo))
					#direcForReportSimple.append(str(todo))
					#simpleCount = simpleCount + 1
					#passs = "no"
					#self.dlg.ui.txtGetDirectionsRSimple.append('\n')
					lngth = 0.0
					road = place[i+1]
					lngth = dist[i+1]
					dd = i
					kk = i + 1
					#if dirAngle < 25:
						#print "in"
					sameRoad = 0
					try:
						while road == place[kk+1]:
							#p1 = angle[dd]
							#p2 = angle[dd + 1]
							# if (p1 > 0 and p2 > 0) or (p1 < 0 and p2 < 0):
							#if p2 > p1:
								#if ((p1 < -90 and p1 > -180) and (p2 > 90 and p2 < 180)):
									#dirAngle = (180 + p1) + (180 - p2)
									#direc = 'turn Left'
								#else:
									#dirAngle = p2 - p1
									#direc = 'turn Right'
							#elif p2 < p1:
								#if ((p1 > 90 and p1 < 180) and (p2 < -90 and p2 > -180)):
									#dirAngle = (180 - p1) + (180 + p2)
									#direc = 'turn Right'
								#else:
									#dirAngle = p1 - p2
									#direc = 'turn Left'
							#else:
								#dirAngle = 0
								#direc = 'go Straight'
							#print str(dirAngle)
							#if dirAngle > 25:
								#break
							#dd = dd + 1
							sameRoad = sameRoad + 1
							kk = kk + 1
					except:
						print "ok"
					showw = str(road) + " , " + str(sameRoad)
					print showw 						
					
					if direc != 'go Straight': #and sameRoad > 1: #and dirAngle > 2:
						#temp 
						direct = "turn "					
						todo = '<b>' + str(direct) + ' onto</b> ' + colorOpen + str(road) + colorClose + '\n'
						wat = 'turn onto'
						what.append(str(wat))
						onRoad.append(str(road))
						#self.dlg.ui.txtGetDirectionsRSimple.append(str(todo))
						#direcForReportSimple.append(str(todo))
						#placeForLabel.append(str(road))
					elif direc == 'go Straight': #and sameRoad > 1: #or dirAngle < 25:
						#if road == place[kk+1]:
						todo = '<b>' + 'Head toward ' + 'on</b> ' + colorOpen + str(road) + colorClose + '\n'
						#elif road != place[kk+1]:
							#print "yes"
							#global passs
							#passs = "yes"
						wat = 'Head toward on'
						what.append(str(wat))
						onRoad.append(str(road))
						#self.dlg.ui.txtGetDirectionsRSimple.append(str(todo))
						#direcForReportSimple.append(str(todo))
						#placeForLabel.append(str(road))
						#simpleCount = simpleCount + 1
					#self.dlg.ui.txtGetDirectionsRSimple.append('\n')					 			
			i = i + 1

		#for a in xrange(len(place)):
			#self.dlg.ui.txtGetDirectionsRSimple.append(str(place[a]))

		#if allStraight == 1:
			#todo = '<b>Continue on road</b> ' + colorOpen + str(road) + colorClose + " , <b>distance</b> : " + colorOpen + str(lngth) + colorClose + " <b>km</b> \n"
			#self.dlg.ui.txtGetDirectionsRSimple.append(str(todo))
		#testing
		#print str(simpleCount)
		#show search button
		self.dlg.ui.btnShowDirOnMap.setVisible(True)
		self.dlg.ui.lblShowDirOnMap.setVisible(True)
		self.dlg.ui.btnStopShowLoc.setVisible(True)

		#while pcountLbl > 1 :
			#pointt1 = QgsPoint(p[pcountLbl-1])
			#plcLbl = self.getPlaceDirName(pointt1)
			#for pp in placeForLabel:
				#if str(pp) == str(plcLbl):
					#pointsRoad.append(pointt1)
					#break
			#pcountLbl = pcountLbl-1

		##self.showRoadsForDirec()
		self.checkDirections()
		self.beforeFlood()
		movie.stop()
		self.dlg.ui.lblLoading.setVisible( False )
		##self.googleDirec()
		self.dlg.ui.btnDirectionstxt.setVisible( True )
		self.dlg.ui.btnDirectionsImage.setVisible( True )
		self.dlg.ui.btnDirectionsPDF.setVisible( True )
		self.dlg.ui.btnDirectionsAudio.setVisible( True )
		self.dlg.ui.lblGenerateDirecFiles.setVisible( True )
		#self.genMapForImage()


    def beforeFlood(self):
	self.dlg.ui.txtGetDirectionsRBefore.clear()
	#find route
	global rdPath
	global layer_path_rd
	if rdPath == '':
		rdPath = layer_path_rd
	print rdPath
	legend = self.iface.legendInterface()
	
	allLayersListNeww = self.iface.legendInterface().layers()
 	for getLayerNew in allLayersListNeww:
		print "inside"
		if str(getLayerNew.source()) == str(rdPath):
			print "here"
		 	vl = getLayerNew

	print vl
	director = QgsLineVectorLayerDirector( vl, -1, '', '', '', 3 )
	properter = QgsDistanceArcProperter()
	director.addProperter( properter )
	crs = self.canvas.mapRenderer().destinationCrs()
	builder = QgsGraphBuilder( crs )	
	global x1
	global y1
	global x2
	global y2
	pStart = QgsPoint( x1, y1 )
	pStop = QgsPoint( x2, y2 )
	print pStart
	print pStop 	
	tiedPoints = director.makeGraph( builder, [ pStart, pStop ] )
	graph = builder.graph()
	tStart = tiedPoints[ 0 ]
	tStop = tiedPoints[ 1 ]
	idStart = graph.findVertex( tStart )
	idStop = graph.findVertex( tStop )
	( tree, cost ) = QgsGraphAnalyzer.dijkstra( graph, idStart, 0 )

	if tree[ idStop ] == -1:
		print "Path not found"
	else:
		pp = []
		curPos = idStop
		
		while curPos != idStart:
			pp.append( graph.vertex( graph.arc( tree[ curPos ] ).inVertex() ).point() )
			curPos = graph.arc( tree[ curPos ] ).outVertex();
		
		pp.append( tStart )
		pcountt = 0
		pcountLbl = 0		
		for pnt in pp:
			print pnt
			pcountt = pcountt +1
	
		print pcountt

		pck = pcountt
		ppk = pp
		tot = 0.0
		while pck > 1 :
			pointt1 = QgsPoint(ppk[pck-1])			
			pointt2 = QgsPoint(ppk[pck-2])
			tot = tot + (self.distance(pointt1.x(), pointt1.y(), pointt2.x(), pointt2.y()))
			pck = pck - 1
		totDisBefore = tot

		anglee = []
		distt = [] 		
		angCountt = 0
		placee = []
		startPlcc = ''
		whatt = []
		onRoadd = []
		disLongg = []
		roadDiss = []
		roadDirr = []
		while pcountt > 1 :
			point1 = QgsPoint(p[pcountt-1])
			print p[pcountt-1]			
			point2 = QgsPoint(p[pcountt-2])
			print p[pcountt-2]
			anglee.append(int(self.getAngle(point1, point2)))
			distt.append(self.distance(point1.x(), point1.y(), point2.x(), point2.y()))
			startPlcc = self.getPlaceDirNameMoreSpecific(point1)
			placee.append(self.getPlaceDirNameMoreSpecific(point1)) ##point2
			var = int(self.getAngle(point1, point2))
			print var
			var2 = self.distance(point1.x(), point1.y(), point2.x(), point2.y())
			print var2
			var3 = self.getPlaceDirNameMoreSpecific(point1)
			print var3
			angCountt = angCountt + 1
			pcountt = pcountt-1

		i = 0
		j = 0 ##
		k = 0 ##
		dirAnglee = 0
		direcc = 'go Straight'
		lengthh = distt[0]
		plcc = placee[0]
		disRounddd = round(lengthh, 2)
		disInMeterss = disRounddd * 1000
		colorOpen = '<font color="blue">'
		colorClose = '</font>'
		self.dlg.ui.txtGetDirectionsRBefore.setText('')
		sameRoad = 3		
		while i < (angCountt-1):##			
			p1 = anglee[i]
			#try:
				#p2 = angle[i + 2]##
				#print "here2"
			#except:
			p2 = anglee[i + 1]
				#print "here1"
			##newly added
			deltaa = p2 - p1
			print deltaa 
			if deltaa < 0:
				deltaa = deltaa + 360 #make sure angle is [0..360]
			
    			if deltaa > 180:
        			direcc = 'turn Left'
    			elif deltaa < 180:
				direcc = 'turn Right'
			else:
				direcc = 'go Straight'

			dirAnglee = p1
			if dirAnglee < 0:
				dirAnglee = dirAnglee + 180
			##newly added above
			#if p2 > p1:
				#if ((p1 < -90 and p1 > -180) and (p2 > 90 and p2 < 180)):
					#dirAngle = (180 + p1) + (180 - p2)
					#direc = 'turn Left'
				#else:
					#dirAngle = p2 - p1
					#direc = 'turn Right'
			#elif p2 < p1:
				#if ((p1 > 90 and p1 < 180) and (p2 < -90 and p2 > -180)):
					#dirAngle = (180 - p1) + (180 + p2)
					#direc = 'turn Right'
				#else:
					#dirAngle = p1 - p2
					#direc = 'turn Left'
			#else:
				#dirAngle = 0
				#direc = 'go Straight'
			lengthh = distt[j]
			#totLen = totLen + length
			disRoundddd = round(lengthh, 2)
			disInMetersss = disRoundddd * 1000
			j = j + 1
			try:			
				plcc = placee[k+2]
			except:
				plcc = placee[k]
			k = k + 1
			newL = '<\n>'	
			print str(p1) + " and " + str(p2)						
			roadDirr.append(str(plcc))
			roadDirr.append(str(direcc))
			# Simplified directions			
			if startPlcc != '':
				if startPlcc == placee[i]: 
					roadd = placee[i]
					#continuer = 'yes'
					lngthh = 0.0
					lngthh = distt[0]
					startPlcc = ''
				else: #unedited
					roadd = placee[i]
					#continuer = 'no'
					lngthh = distt[0]
					startPlcc = ''

			if placee[i] == placee[i+1]:
				#road = place[i+1]
				roadd = placee[i]
				#lngth = dist[i+1]
				lngthh = lngthh + distt[i+1]
				if i == angCountt-2: # for last record
					disRoundd = round(lngthh, 2)
					roadDiss.append(str(roadd))
					roadDiss.append(disRoundd)
			else:
				if 1 > 0: # false if (no need)
					#global passs
					print "comee"
					##global lngthh
					#allStraight = 0
					disRoundd = round(lngthh, 2)
					watt = 'Continue on'
					whatt.append(str(watt))
					onRoadd.append(str(roadd))
					disLongg.append(str(disRoundd))
					roadDiss.append(str(roadd))
					roadDiss.append(disRoundd)
					lngthh = 0.0
					roadd = placee[i+1]
					lngthh = distt[i+1]
					ddd = i
					kkk = i + 1
					#if dirAngle < 25:
						#print "in"
					sameRoadd = 0
					try:
						while roadd == placee[kkk+1]:
							sameRoadd = sameRoadd + 1
							kkk = kkk + 1
					except:
						print "ok"
					##showw = str(road) + " , " + str(sameRoad)
					##print showw 						
					
					if direcc != 'go Straight': #and sameRoad > 1: #and dirAngle > 2:
						#temp 
						directt = "turn "					
						##todo = '<b>' + str(direct) + ' onto</b> ' + colorOpen + str(road) + colorClose + '\n'
						watt = 'turn onto'
						whatt.append(str(watt))
						onRoadd.append(str(roadd))
						#self.dlg.ui.txtGetDirectionsRSimple.append(str(todo))
						#direcForReportSimple.append(str(todo))
						#placeForLabel.append(str(road))
					elif direcc == 'go Straight': #and sameRoad > 1: #or dirAngle < 25:
						#if road == place[kk+1]:
						##todo = '<b>' + 'Head toward ' + 'on</b> ' + colorOpen + str(road) + colorClose + '\n'
						#elif road != place[kk+1]:
							#print "yes"
							#global passs
							#passs = "yes"
						watt = 'Head toward on'
						whatt.append(str(watt))
						onRoadd.append(str(roadd))
						#self.dlg.ui.txtGetDirectionsRSimple.append(str(todo))
						#direcForReportSimple.append(str(todo))
						#placeForLabel.append(str(road))
						#simpleCount = simpleCount + 1
					#self.dlg.ui.txtGetDirectionsRSimple.append('\n')					 			
			i = i + 1

	simpleCountt = 0

	#eliminate miss directions
	i = 0
	while i < len(whatt):
		curRoadd = onRoadd[i]
		#i = i + 4
		j = i + 1		
		while j < len(whatt):
			if str(onRoadd[j]) != str(curRoadd):			
				j = j + 1
				continue
			elif str(onRoadd[j]) == str(curRoadd):
				if str(whatt[j]) != "Continue on":
					j = j + 1
					continue
				else:
					k = j
					while k != i+1:
						del onRoadd[k-1]
						del whatt[k-1]
						k = k - 1
					break
		i = i + 1	

	
	for i in xrange(len(whatt)):
		kk = str(whatt[i]) + " " + str(onRoadd[i])
		print kk
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(kk))

	
	#eliminate duplicate roads
	uniRr = []
	uniRr.append( onRoadd[0] )
	dk = 0
	while dk < len(onRoadd):
		if not onRoadd[dk] in uniRr:
			uniRr.append(onRoadd[dk])
		dk = dk + 1	

	
	for ii in xrange(len(uniRr)):
		kkk = str(uniRr[ii])
		print kkk
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(uniR[ii]))

	#for ii in xrange(len(roadDis)):
		#kkk = str(uniW[ii]) + " " + str(uniR[ii])
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(roadDis[ii]))

	#get distances
	disStt = []
	tot = 0.0
	rd = 0
	ss = 0
	while rd < len(uniRr):
		curr = uniRr[rd]
		tot = 0.0
		ss = 0
		while ss < len(roadDiss):		
			nww = roadDiss[ss]
			if str(curr) == str(nww):			
				diss = roadDiss[ss+1]
				tot = tot + diss
			ss = ss + 1
		disStt.append(tot)		
		rd = rd + 1
		
	
	for ij in xrange(len(disStt)):
		kkk = str(uniRr[ii])
		print kkk
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(disSt[ij]))

	#get directions - turn onto
	direCc = []
	c = 0
	e = 1
	while e < len(uniRr):
		nWw = uniRr[e]
		c = 0
		while c < len(roadDirr):
			topp = roadDirr[c]
			if str(nWw) == str(topp):
				direCttt = roadDirr[c+1]##
				direCc.append(str(direCttt))
				break
			c = c + 1	
		e = e + 1


	for ij in xrange(len(direCc)):
		print ij
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(direC[ij]))


	colorOpen = '<font color="blue">'
	colorClose = '</font>'
	colorOpenR = '<font color="red">'
	colorCloseR = '</font>'
	bolds = '<b>'
	bolde = '</b>'
	r = 0
	while r < len(disStt):
		try:
			print "while"
			prnt1 =  '<b>Continue on</b> ' + colorOpen + str(uniRr[r]) + colorClose + " , <b>distance</b> : " + colorOpen + str(disStt[r]) +  colorClose + " <b>km</b>"
			##direcForReportSimple.append(str(prnt1))
			simpleCountt = simpleCountt + 1
			prnt2 = '<b>' + str(direCc[r]) + ' onto</b> ' + colorOpen + str(uniRr[r+1]) + colorClose
			##direcForReportSimple.append(str(prnt2))
			simpleCountt = simpleCountt + 1
			self.dlg.ui.txtGetDirectionsRBefore.append(str(prnt1))
			self.dlg.ui.txtGetDirectionsRBefore.append(str(prnt2))
			print r
			r = r + 1
		except:
			break			
			e = sys.exc_info()[0]
			print e
			
	print "out"
	last = '<b>Continue on</b> ' + colorOpen + str(uniRr[(len(uniRr)-1)]) + colorClose + " , <b>distance</b> : " + colorOpen + str(disStt[(len(disStt)-1)]) +  colorClose + " <b>km</b>"
	self.dlg.ui.txtGetDirectionsRBefore.append(str(last))
	#direcForReportSimple.append(str(last))
	#simpleCount = simpleCount + 1

	##Fill summary##
	self.dlg.ui.txtGetDirectionsR.clear()
	dKmH = 25 #25kmh
	dMilesH = dKmH * 0.621371 #miles/h
	#time	
	time = totDisBefore / dKmH
	timeRound = round(time, 2)
	print timeRound
	hrs = int(timeRound)
	number_dec = str(timeRound-int(timeRound))[1:]
	#print number_dec
	mins = float(number_dec) * 60
	minutes = int(mins)
	print hrs
	print mins
	print int(mins)
	global ds
	global nowHrs
	global nowMins
	befDis = '<b>Total distance had to travel</b> : ' + colorOpen + str(totDisBefore) + colorClose +' <b>km</b> '
	befTime = '<b>Total time taken ( 25kmph )</b>  : ' + colorOpen + str(hrs) + colorClose +' <b>hour(s)</b> and ' + colorOpen + str(minutes) + colorClose + ' <b>minute(s)</b> '
	nowDis = '<b>Total distance have to travel</b> : ' + colorOpen + str(ds) + colorClose +' <b>km</b> '
	nowTime = '<b>Total time takes ( 25kmph )</b>  : ' + colorOpen + str(nowHrs) + colorClose + ' <b>hour(s)</b> and ' + colorOpen + str(nowMins) + colorClose + ' <b>minute(s)</b> '
	disDiff = ds - totDisBefore
	if disDiff > 0:
		ml = ' MORE '
	else:
		ml = ' LESS '
	disDiffD = '<b>You have to travel</b> ' + colorOpen + bolds + str(ml) + bolde + colorClose + colorOpenR + ' <b>Today</b> : ' + colorCloseR + str(disDiff) + ' <b>km</b> ' 
	global startName
	global stopName
	selPath = "<b>From</b> : " + str(startName) + " , <b>To</b> : " + str(stopName)	
	self.dlg.ui.txtGetDirectionsR.setText(str(selPath))
	self.dlg.ui.txtGetDirectionsR.append('')
	self.dlg.ui.txtGetDirectionsR.append(colorOpenR + '<b>Earlier</b> ' + colorCloseR) 
	self.dlg.ui.txtGetDirectionsR.append(str(befDis))
	self.dlg.ui.txtGetDirectionsR.append(str(befTime))
	self.dlg.ui.txtGetDirectionsR.append('')
	self.dlg.ui.txtGetDirectionsR.append(colorOpenR + '<b>Today</b> ' + colorCloseR)
	self.dlg.ui.txtGetDirectionsR.append(str(nowDis))
	self.dlg.ui.txtGetDirectionsR.append(str(nowTime))
	self.dlg.ui.txtGetDirectionsR.append('')
	self.dlg.ui.txtGetDirectionsR.append(str(disDiffD))




    def googleDirec(self):
	try:
		global startLabel
		global stopLabel
		colorOpen = '<font color="blue">'
		colorClose = '</font>'
		self.dlg.ui.txtGetDirectionsRBefore.clear()
		self.dlg.ui.txtGetDirectionsRBefore.setText('')
		origin = str(startLabel) 
		destination = str(stopLabel) 
		#self.dlg.ui.txtGetDirectionsRBefore.append(str(origin))
		#self.dlg.ui.txtGetDirectionsRBefore.append(str(destination))
		mapService = GoogleMaps()
		directions = mapService.directions(origin,destination)
		distance = directions['Directions']['Distance']['meters']
		time = directions['Directions']['Duration']['seconds']
		lengtH = distance / 1000.0
		disttRound = round(lengtH, 1)
		tim = time/60.0
		prnt1 = "<b>Total Distance</b> : " + colorOpen + str(disttRound) + colorClose + " <b>km</b>"
		prnt2 = "<b>Travel Time</b> : " + colorOpen + str(int(tim)) + colorClose + " <b>minutes</b>\n"
		#self.dlg.ui.txtGetDirectionsRBefore.append('\n')
		prnt3 = colorOpen + "<b>Directions</b>\n"	+ colorClose
		#self.dlg.ui.txtGetDirectionsRBefore.append('\n')
		#self.dlg.ui.txtGetDirectionsRBefore.append(str(distance))
		self.dlg.ui.txtGetDirectionsRBefore.append(prnt1)
		self.dlg.ui.txtGetDirectionsRBefore.append(prnt2)
		self.dlg.ui.txtGetDirectionsRBefore.append(prnt3)
		for step in directions['Directions']['Routes'][0]['Steps']:
			print self.strip_tags(step['descriptionHtml'])
			self.dlg.ui.txtGetDirectionsRBefore.append(step['descriptionHtml'])
	except:
		colorR = '<font color="red">'
		colorRs = '</font>'
		err1 = colorR + "<b>Problem Retrieving Data<b>" + colorRs
		err2 = "<b>1</b>. Check your Internet Connection "
		err3 = "<b>2</b>. Check again the Origin and Destination "
		self.dlg.ui.txtGetDirectionsRBefore.setText(str(err1))
		self.dlg.ui.txtGetDirectionsRBefore.append(str(err2))
		self.dlg.ui.txtGetDirectionsRBefore.append(str(err3))		


    def generatetxtDirec(self):
	global direcForReportSimple
	global startName
	global stopName
	global direcFilesID
	direcFilesID = direcFilesID + 1
	#global startLabel
	#global stopLabel
	#self.dlg.ui.txtGetDirectionsRBefore.clear()
	#self.dlg.ui.txtGetDirectionsRBefore.setText('')
	#origin = str(startLabel)
	#destination = str(stopLabel)
	#mapService = GoogleMaps()
	#directions = mapService.directions(origin,destination)
	
	#with open('directions.txt','w')	as f:
		#for step in directions['Directions']['Routes'][0]['Steps']:
			#f.write(self.strip_tags(step['descriptionHtml'] + '\r\n'))
	global filePath
	filePath = '/home/kasun/directions_FLOOgin_'+ str(direcFilesID)
	if not os.path.exists(str(filePath)):
		os.makedirs(str(filePath))
	global txtPath
	txtPath = str(filePath) + '/directions_FLOOgin.txt'
	direc = 'Directions from ' + str(startName) + ' to ' + str(stopName)
	with open('directions_FLOOgin.txt','w')	as f:
		f.write(self.strip_tags(str(direc) + '. \r\n\n'))
		for step in xrange(len(direcForReportSimple)):
			f.write(self.strip_tags(str(direcForReportSimple[step]) + '. \r\n\n'))
		f.write(' Thank You for using FLaagin . Have a nice day. ')	
	src = 'directions_FLOOgin.txt'
	dst = str(filePath)
	self.copyFile(src,dst)
	webbrowser.open(str(txtPath))
	#self.generateAudioDirections()
		

    def generateAudioDirections(self):
	#def get_my_string():
    		#inputFn = "/home/kasun/directions_FLOOgin.txt"
		#with open(inputFn) as inputFileHandle:
        		#return inputFileHandle.read()
	#self.googletts.audio_extract(input_text=get_my_string(), args = {'language':'en','output':'directions_FLOOgin.mp3'})
	#execfile("GoogleTTS.py")
	global filePath
	try:	
		subprocess.call("./FLOOgin/floogin/GoogleTTS.py", shell=True)
		src = 'directions_FLOOgin.mp3'
		dst = str(filePath)
		self.copyFile(src, dst)
		colB = '<font color="blue">'
		colBs = '</font>'	
		textToShow = "Audio File Generated Successfully" 
		textSub = "Saved in " + colB + str(filePath) + colBs +" as directions_FLOOgin.mp3 "
		msgBox = QtGui.QMessageBox()
 		msgBox.setText(str(textToShow))
 		msgBox.setInformativeText(str(textSub))
 		msgBox.setStandardButtons(QMessageBox.Ok)
		msgBox.setWindowTitle("Generate Audio File")
 		ret = msgBox.exec_();
	except:
		##check again
		colR = '<font color="red">'
		colRs = '</font>'	
		textToShow = colR + "Problem Generating Audio File" + colRs 
		textSub = "Please check your Internet Connection an try again "
		msgBox = QtGui.QMessageBox()
 		msgBox.setText(str(textToShow))
 		msgBox.setInformativeText(str(textSub))
 		msgBox.setStandardButtons(QMessageBox.Ok)
		msgBox.setWindowTitle("Generate Audio File - Error")
 		ret = msgBox.exec_();
		

    def get_my_string():
    	inputFn = "/home/kasun/directions_FLOOgin.txt"

    	with open(inputFn) as inputFileHandle:
        	return inputFileHandle.read()

    def copyFile(self,src, dst):
    	try:
    	    shutil.copytree(src, dst)
    	except OSError as exc: # python >2.5
    	    if exc.errno == errno.ENOTDIR:
    	        shutil.copy(src, dst)
    	    else: raise

    def checkDirections(self):
	global direcForReportSimple
	global what
	global onRoad
	global disLong
	global roadDis
	global roadDir
	global simpleCount		
	simpleCount = 0
	direcForReportSimple = []
	#s1 = str(len(what))
	#s2 = str(len(onRoad))
	#s3 = str(len(disLong))
	#self.dlg.ui.txtGetDirectionsRSimple.append("**************")
	#self.dlg.ui.txtGetDirectionsRSimple.append(s1)
	#self.dlg.ui.txtGetDirectionsRSimple.append(s2)
	#self.dlg.ui.txtGetDirectionsRSimple.append(s3)
	#for i in xrange(len(what)):
		#kk = str(what[i]) + " " + str(onRoad[i])
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(kk))
	#for j in disLong:
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(j))

	#eliminate miss directions
	i = 0
	while i < len(what):
		curRoad = onRoad[i]
		#i = i + 4
		j = i + 1		
		while j < len(what):
			if str(onRoad[j]) != str(curRoad):			
				j = j + 1
				continue
			elif str(onRoad[j]) == str(curRoad):
				if str(what[j]) != "Continue on":
					j = j + 1
					continue
				else:
					k = j
					while k != i+1:
						del onRoad[k-1]
						del what[k-1]
						k = k - 1
					break
		i = i + 1	

		#try:
			#if str(curRoad) == str(onRoad[i]):
				#del onRoad[i-1]
				#del onRoad[i-2]
				#del onRoad[i-3]
				#del what[i-1]
				#del what[i-2]
				#del what[i-3]
		#except:
			#e = sys.exc_info()[0]
			#print e
	
	#for i in xrange(len(what)):
		#kk = str(what[i]) + " " + str(onRoad[i])
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(kk))


	#self.dlg.ui.txtGetDirectionsRSimple.append("#################")
	
	#eliminate duplicate roads
	uniR = []
	uniR.append( onRoad[0] )
	dk = 0
	while dk < len(onRoad):
		if not onRoad[dk] in uniR:
			uniR.append(onRoad[dk])
		dk = dk + 1	

	#uniW = []	
	#dd = 0
	#while dd < len(what):
		#try:
			#now = what[ dd ]
			#next = what[ dd + 1 ]
			#if str(now) == str(next):
				#if str(now) != str(what[ dd - 1 ]):
					#uniW.append(what[ dd ])
			#else:
				#uniW.append(what[ dd ])
				#uniW.append(what[ dd + 1 ])
		
			#dd = dd + 1
		#except:
			#e = sys.exc_info()[0]
			#print e

	#self.dlg.ui.txtGetDirectionsRSimple.append(str(len(uniW)))
	#self.dlg.ui.txtGetDirectionsRSimple.append(str(len(uniR)))
	
	#for ii in xrange(len(uniR)):
		#kkk = str(uniW[ii]) + " " + str(uniR[ii])
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(uniR[ii]))

	#for ii in xrange(len(roadDis)):
		#kkk = str(uniW[ii]) + " " + str(uniR[ii])
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(roadDis[ii]))

	#get distances
	disSt = []
	tot = 0.0
	rd = 0
	ss = 0
	while rd < len(uniR):
		cur = uniR[rd]
		tot = 0.0
		ss = 0
		while ss < len(roadDis):		
			nw = roadDis[ss]
			if str(cur) == str(nw):			
				dis = roadDis[ss+1]
				tot = tot + dis
			ss = ss + 1
		disSt.append(tot)		
		rd = rd + 1
		
	
	#for ij in xrange(len(disSt)):
		#kkk = str(uniW[ii]) + " " + str(uniR[ii])
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(disSt[ij]))

	#get directions - turn onto
	direC = []
	c = 0
	e = 1
	while e < len(uniR):
		nW = uniR[e]
		c = 0
		while c < len(roadDir):
			top = roadDir[c]
			if str(nW) == str(top):
				direCtt = roadDir[c+1]##
				direC.append(str(direCtt))
				break
			c = c + 1	
		e = e + 1


	#for ij in xrange(len(direC)):
		#self.dlg.ui.txtGetDirectionsRSimple.append(str(direC[ij]))


	colorOpen = '<font color="blue">'
	colorClose = '</font>'
	r = 0
	while r < len(disSt):
		try:
			prnt1 =  '<b>Continue on</b> ' + colorOpen + str(uniR[r]) + colorClose + " , <b>distance</b> : " + colorOpen + str(disSt[r]) +  colorClose + " <b>km</b>"
			direcForReportSimple.append(str(prnt1))
			simpleCount = simpleCount + 1
			prnt2 = '<b>' + str(direC[r]) + ' onto</b> ' + colorOpen + str(uniR[r+1]) + colorClose
			direcForReportSimple.append(str(prnt2))
			simpleCount = simpleCount + 1
			self.dlg.ui.txtGetDirectionsRSimple.append(str(prnt1))
			self.dlg.ui.txtGetDirectionsRSimple.append(str(prnt2))
			r = r + 1
		except:
			break
			e = sys.exc_info()[0]
			print e

	last = '<b>Continue on</b> ' + colorOpen + str(uniR[(len(uniR)-1)]) + colorClose + " , <b>distance</b> : " + colorOpen + str(disSt[(len(disSt)-1)]) +  colorClose + " <b>km</b>"
	self.dlg.ui.txtGetDirectionsRSimple.append(str(last))
	#direcForReportSimple.append(str(last))
	#simpleCount = simpleCount + 1



    def showRoadsForDirec(self):
	global pointsRoad
	#global placeForLabel
	global place
	global vll
	global tempLayerRds
	tempLayerRds = "temporary_points"
	# create layer
	vll = QgsVectorLayer("Point?crs=epsg:4326", "temporary_points", "memory")
	pr = vll.dataProvider()
	# add fields
	vll.startEditing()
	pr.addAttributes( [ QgsField("name", QVariant.String) ] )
	# add a feature
	for i in xrange(len(place)):
		fet = QgsFeature()
		fet.setGeometry( QgsGeometry.fromPoint( pointsRoad[i] ))
		fet.setAttributes([str(place[i])])
		pr.addFeatures([fet])

	# update layer’s extent when new features have been added
	# because change of extent in provider is not propagated to the layer
	vll.updateExtents()
	vll.commitChanges()
	#verify layer craeted
	print "fields:", len(pr.fields())
	print "features:", pr.featureCount()
	f = QgsFeature()
	features = vll.getFeatures()
	for f in features:
		print "F:",f.id(), f.attributes(), f.geometry().asPoint()
	QgsMapLayerRegistry.instance().addMapLayer(vll)


	palyrr = QgsPalLayerSettings()
	palyrr.readFromLayer(vll)
	palyrr.enabled = True
	palyrr.fieldName = 'name'
	palyrr.placement = QgsPalLayerSettings.AroundPoint
	palyrr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
	#palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
	palyrr.writeToLayer(vll)
	self.canvas.refresh()
	





    def showDirecOnMap(self):
	self.labelPos.clear()
	global stopPlaceDir
	stopPlaceDir = 1	
	self.placeForDir()	

    def placeForDir(self):
		sizeOp = '<h2>'
		sizeCl = '<\h2>'
		#self.labelPos.setVisible(False)
		global stopPlaceDir
		#self.clickTool.canvasClicked.connect(self.clickedCanvas)
		while stopPlaceDir == 1:
			try:		
				global stopPlaceDir
				#self.labelPos.setText(str(plce))
				#global plce
				#global cur
				#self.labelPos.clear()
				cur = self.iface.mapCanvas().mouseLastXY()
				#global curX
				#global curY	 
				curX = cur.x()
				curY = cur.y()
				self.labelPos.setGeometry(QtCore.QRect(0 ,0, 600, 100))		
				myMapToPixel = self.iface.mapCanvas().getCoordinateTransform()
				#QPoint(cur)
				xy = myMapToPixel.toMapCoordinates(cur)
				#self.addLabel()
				#print xy
				pointt = QgsPoint(xy)
				plce = self.getPlaceDirName(pointt)
				#sizeOp = '<h2>'
				#sizeCl = '<\h2>'
				plceName = sizeOp + "<b>Location :</b> " + str(plce) + sizeCl
				print plceName
				#self.dlg.setTextBrowserDesStart(str(plceName))
				#lp = plceName
				#lp = 0			
				#while lp < 5000:
					#lp = lp + 1
		        	#self.labelPos.setGeometry(QtCore.QRect(cur.x(),cur.y(), 150, 25))
        			#font = QtGui.QFont()
        			#font.setPointSize(16)
        			#font.setBold(True)
        			#font.setWeight(75)
        			#self.labelPos.setFont(font)
				self.labelPos.setVisible(True)
				#self.labelPos.clear()	
				self.labelPos.setText(str(plceName))
				#self.labelPos.setVisible(False)			
				#self.pointCursor()
				#self.clickTool.canvasClicked.connect(self.clickedCanvas)
				#self.place()
			except:
				e = sys.exc_info()[0]
				print e
				#self.place()
		self.labelPos.clear()




    def getPlaceDirName(self, point):
		# setup the provider select to filter results based on a rectangle
       		pntGeom = QgsGeometry.fromPoint(point)
       		# scale-dependent buffer of 2 pixels-worth of map units
       		pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       		rect = pntBuff.boundingBox()
       		# get currentLayer and dataProvider
       		cLayer = self.canvas.currentLayer()
		self.provider = cLayer.dataProvider()
              	request = QgsFeatureRequest().setFilterRect(rect)
		try:
 	    		feature = cLayer.getFeatures(request).next()
		#except StopIteration:
			#print "Feature not found"
			#nIndx = self.provider.fieldNameIndex('NAME')
			#fields = cLayer.pendingFields()
			#firstCol = str(fields.field(0).name()) + " : " + str(feature[0])
			fieldNm = self.getFieldName(cLayer)
			#if nIndx != -1:
	   		featrGot = feature[fieldNm]
			featr = str(featrGot)   
			#else:
			#featr = firstCol
			return featr
		except StopIteration:
			print "Feature not found"		

    def getPlaceDirNameMoreSpecific(self, point):
		# setup the provider select to filter results based on a rectangle
       		pntGeom = QgsGeometry.fromPoint(point)
       		# scale-dependent buffer of 2 pixels-worth of map units
       		pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 0.0001),0)
       		rect = pntBuff.boundingBox()
       		# get currentLayer and dataProvider
       		cLayer = self.canvas.currentLayer()
		self.provider = cLayer.dataProvider()
              	request = QgsFeatureRequest().setFilterRect(rect)
		try:
 	    		feature = cLayer.getFeatures(request).next()
		#except StopIteration:
			#print "Feature not found"
			#nIndx = self.provider.fieldNameIndex('NAME')
			#fields = cLayer.pendingFields()
			#firstCol = str(fields.field(0).name()) + " : " + str(feature[0])
			fieldNm = self.getFieldName(cLayer)
			#if nIndx != -1:
	   		featrGot = feature[fieldNm]
			featr = str(featrGot)   
			#else:
			#featr = firstCol
			return featr
		except StopIteration:
			print "Feature not found"		



    def getPlaceDir(self, point):
		# setup the provider select to filter results based on a rectangle
       		pntGeom = QgsGeometry.fromPoint(point)
       		# scale-dependent buffer of 2 pixels-worth of map units
       		pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       		rect = pntBuff.boundingBox()
       		# get currentLayer and dataProvider
       		cLayer = self.canvas.currentLayer()
		self.provider = cLayer.dataProvider()
              	request = QgsFeatureRequest().setFilterRect(rect)
		try:
 	    		feature = cLayer.getFeatures(request).next()
		#except StopIteration:
			#print "Feature not found"
			#nIndx = self.provider.fieldNameIndex('NAME')
			#fields = cLayer.pendingFields()
			#firstCol = str(fields.field(0).name()) + " : " + str(feature[0])
			fieldNm = self.getFieldName(cLayer)
			#if nIndx != -1:
	   		featrGot = feature[fieldNm]
			featr = str(fieldNm) + " : " + str(featrGot)   
			#else:
			#featr = firstCol
			return featr
		except StopIteration:
			print "Feature not found"		

    def fillDirecDetails(self):
	global startName
	global stopName
	#global totLen
	selPath = "<b>From</b> : "+ str(startName) + " , <b>To</b> : " + str(stopName)	
	self.dlg.ui.txtSelectPathR.setText(str(selPath))
	global pcount
	global p
	pc = pcount
	pp = p
	#global dist
	#i = 0
	tot = 0.0
	#while i < (pcount):
		#tot = tot + dist[i]
		#i = i + 1
	##global x1
	##global y1
	##global x2
	##global y2
	global ds
	##ds = self.distance(x1, y1, x2, y2)
	#ds = tot
	while pc > 1 :
		point1 = QgsPoint(pp[pc-1])			
		point2 = QgsPoint(pp[pc-2])
		tot = tot + (self.distance(point1.x(), point1.y(), point2.x(), point2.y()))
		pc = pc - 1
	ds = tot
	self.dlg.ui.txtLengthR.setText(str(ds))

#	lengthMet = self.dlg.ui.cmbLength2R.currentText()
#	if lengthMet == 'km':
#		self.dlg.ui.txtLengthR.setText(str(ds))
#	elif lengthMet == 'm':
#		dsM = ds * 1000
#		self.dlg.ui.txtLengthR.setText(str(dsM))


    def lenMetricIndexChanged(self):
		global ds
		lengthMet = self.dlg.ui.cmbLength2R.currentText()
		if lengthMet == 'km':
			self.dlg.ui.txtLengthR.setText(str(ds))
		elif lengthMet == 'm':
			dsM = ds * 1000
			self.dlg.ui.txtLengthR.setText(str(dsM))
		elif lengthMet == 'mile':
			dsMile = ds * 0.621371
			self.dlg.ui.txtLengthR.setText(str(dsMile))

    def ClearGetDir(self):
		self.dlg.ui.txtSelectPathR.clear()
		self.dlg.ui.txtGetDirectionsR.clear()
		self.dlg.ui.txtGetDirectionsRSimple.clear()
		self.dlg.ui.txtGetDirectionsRBefore.clear()
		self.dlg.ui.cmbLength2R.setCurrentIndex(0)
		self.dlg.ui.txtLengthR.clear()
		self.dlg.ui.lblLoading.setVisible( False )
		#time to travel
		self.dlg.ui.txtSpeedMph.clear()
		self.dlg.ui.txtTimeToTravelHrs.clear()
		self.dlg.ui.txtTimeToTravelMins.clear()
		self.dlg.ui.btnShowDirOnMap.setVisible(False)
		self.dlg.ui.lblShowDirOnMap.setVisible(False)
		self.dlg.ui.btnStopShowLoc.setVisible(False)
		self.dlg.ui.btnDirectionstxt.setVisible(False)
		self.dlg.ui.btnDirectionsImage.setVisible(False)
		self.dlg.ui.btnDirectionsPDF.setVisible(False)
		self.dlg.ui.btnDirectionsAudio.setVisible(False)
		self.dlg.ui.lblGenerateDirecFiles.setVisible(False)
		self.labelPos.clear()
		global stopPlaceDir
		stopPlaceDir = 0

		try:
			global vll
			palyrr = QgsPalLayerSettings()
			palyrr.readFromLayer(vll)
			palyrr.enabled = False
			palyrr.fieldName = 'name'
			palyrr.placement = QgsPalLayerSettings.OverPoint
			palyrr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
			# palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
			palyrr.writeToLayer(vll)
			self.canvas.refresh()
		
			#global tempLayerRds
			#legendD = self.iface.legendInterface()
			#allLayersListNewW = self.canvas.layers()
 			#for getLayerNewW in allLayersListNewW:
				#if str(getLayerNewW.name()) == str(tempLayerRds):
					#legendD.setLayerVisible(getLayerNewW, False)
		except:
			print "clear"



	##*************************************************keywords

    def generateMap(self):
	try:
		self.keywords_from_layers()
	except:
		e = sys.exc_info()[0]
		print e
		colR = '<font color="red">'
		colRs = '</font>'	
		textToShow = "Sorry. No " + colR + ".keywords " + colRs + "files found" 
		textSub = "Please select the relevant layers from drop downs and generate map manually"
		msgBox = QtGui.QMessageBox()
 		msgBox.setText(str(textToShow))
 		msgBox.setInformativeText(str(textSub))
 		msgBox.setStandardButtons(QMessageBox.Ok)
		msgBox.setWindowTitle("No Keywords Found Error")
 		ret = msgBox.exec_();

		

    def generateMapManually(self):
#	allLayersLoaded = self.canvas.layers()
# 	for SelLayer in allLayersLoaded:	
#		self.dlg.ui.cboRoadLayer.addItem(SelLayer.name())
#                self.dlg.ui.cboFloodLayer.addItem(SelLayer.name())
	global roadLayer
	global floodLyrForRpt 	
	roadLayer = self.dlg.ui.cboRoadLayer.currentText()	
	global floodLayer
	global rdPath
	global fdPath
	floodLayer = self.dlg.ui.cboFloodLayer.currentText()
	floodLyrForRpt = str(floodLayer)
	outputFile = self.dlg.ui.leOutputFile.text()
	allLayersList = self.canvas.layers()
 	for getLayer in allLayersList:
		if str(getLayer.name()) == str(roadLayer):
			rdPath = str(getLayer.source())
		elif str(getLayer.name()) == str(floodLayer):
			fdPath = str(getLayer.source())
	output = os.path.splitext(rdPath)[0]
	output += '_'+outputFile+'.shp'
	## processing.runandload("qgis:difference", rdPath, fdPath, output)
	processing.runalg("qgis:difference", rdPath, fdPath, output)
	wb = QgsVectorLayer(output, outputFile, 'ogr')
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
		#change color
		symbols = wb.rendererV2().symbols()
		symbol = symbols[0]
		symbol.setColor(QtGui.QColor.fromRgb(0,170,0))
		self.canvas.refresh() 
		self.iface.legendInterface().refreshLayerSymbology(wb)
	else:
		print "No layer found"

	#active new layer   
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
 	for getLayerNew in allLayersListNew:
		if str(getLayerNew.name()) == str(outputFile):
			legend.setLayerVisible(getLayerNew, True)
		elif str(getLayerNew.name()) == str(floodLayer):
			legend.setLayerVisible(getLayerNew, True)
			#change color
			lyrr = self.getLayerByName( getLayerNew.name() )
			symbols = lyrr.rendererV2().symbols()
			symbol = symbols[0]
			symbol.setColor(QtGui.QColor.fromRgb(0,120,255))
			self.canvas.refresh() 
			self.iface.legendInterface().refreshLayerSymbology(lyrr)
		else: 
			legend.setLayerVisible(getLayerNew, False)
	

	
    def clearGenMapFields(self):
	self.dlg.ui.leOutputFile.clear()
	self.dlg.ui.cboRoadLayer.clear()
        self.dlg.ui.cboFloodLayer.clear()

	allLayersIn = self.canvas.layers()
 	for LayerNow in allLayersIn:	
		self.dlg.ui.cboRoadLayer.addItem(LayerNow.name())
                self.dlg.ui.cboFloodLayer.addItem(LayerNow.name())
	colRd = '<font color="red">'
	colRds = '</font>'
	self.dlg.ui.txtFirstSteps.clear()
	self.dlg.ui.txtFirstSteps.setText(colRd + "<b>Please follow these steps</b>" + colRds + '\n' + "<b>(Press on down arrow to start)</b>")
	global n
	n = 0
	global now
	now = 2



    def keywords_from_layers(self):
	allLayers = self.canvas.layers()
 	for oneLayer in allLayers:	
		self.layer = oneLayer
		self.load_state_from_keywords()
	global layer_path_haz
	global layer_path_rd
	global roadLayer
	#print layer_path_haz
	#print layer_path_rd
        #print layer_path_haz
	result_file_path = os.path.splitext(layer_path_rd)[0]
	roadLayer = result_file_path
        result_file_path += '_flood_affect.shp'
	##processing.runandload("qgis:difference", layer_path_rd, layer_path_haz, result_file_path)
	#movie = QtGui.QMovie(":/plugins/floogin/loading1.gif")
	#self.dlg.ui.lblLoading.setMovie(movie)
	#movie.start()
	processing.runalg("qgis:difference", layer_path_rd, layer_path_haz, result_file_path)
	#movie.stop()
	wb = QgsVectorLayer(result_file_path, 'Roads_safe', 'ogr')
	if wb.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(wb)
		#change color
		symbols = wb.rendererV2().symbols()
		symbol = symbols[0]
		symbol.setColor(QtGui.QColor.fromRgb(0,170,0))
		self.canvas.refresh() 
		self.iface.legendInterface().refreshLayerSymbology(wb)
		print "hi"		
		#self.label(wb)
	else:
		print "No layer found"

	#active New Layer
	#global floodLayer
	#print floodLayer
	legend = self.iface.legendInterface()
	allLayersListNew = self.canvas.layers()
	outFile = 'Roads_safe'
 	for getLayerNew in allLayersListNew:
		if str(getLayerNew.name()) == str(outFile):
			legend.setLayerVisible(getLayerNew, True)
		elif str(getLayerNew.source()) == str(layer_path_haz):
			legend.setLayerVisible(getLayerNew, True)
			#change color
			lyr = self.getLayerByName( getLayerNew.name() )
			symbols = lyr.rendererV2().symbols()
			symbol = symbols[0]
			symbol.setColor(QtGui.QColor.fromRgb(0,120,255))
			self.canvas.refresh() 
			self.iface.legendInterface().refreshLayerSymbology(lyr)
		else: 
			legend.setLayerVisible(getLayerNew, False)
	


#    def category_from_keywords(self):
#        """Set the ui state to match the keywords of the active layer.

#        In case the layer has no keywords or any problem occurs reading them,
#        start with a blank slate so that subcategory gets populated nicely &
#        we will assume exposure to start with.

#        Also if only title is set we use similar logic (title is added by
#        default in dock and other defaults need to be explicitly added
#        when opening this dialog). See #751

#        """
        #keywords = {'category': 'exposure'}

#	allLayers = self.canvas.layers()
#	for layer in allLayers:
#        	try:
            	# Now read the layer with sub layer if needed
#			global source			
#			source = str(layer.source())            		
#			keywords = self.read_keywords(layer)
#        	except (InvalidParameterError,
#                	HashNotFoundError,
#                	NoKeywordsFoundError):
#            		pass
        #layer_name = self.layer.name()
        #if 'title' not in keywords:
        #    self.leTitle.setText(layer_name)
        #self.lblLayerName.setText(self.tr('Keywords for %s' % layer_name))

        #if 'source' in keywords:
        #    self.leSource.setText(keywords['source'])
        #else:
        #    self.leSource.setText('')

        # if we have a category key, unpack it first
        # so radio button etc get set
#        	if 'category' in keywords:
#	     		cat = keywords['category']
#       			if cat == 'hazard':
#				layerType = 'hazard'
#				layer_name_haz = self.layer.name()
#				layer_path_haz = str(self.layer.source())
#				print layer_path_haz
#			if cat == 'exposure':
#				layerType = 'exposure'
#				layer_name_rd = self.layer.name()
#				layer_path_rd = str(self.layer.source())
#				print layer_path_rd	
        #    self.set_category(keywords['category'])
        #    keywords.pop('category')
#        	else:
#			layerType = 'exposure'
           # assume exposure to match ui. See issue #751
        #    self.add_list_entry('category', 'exposure')
	
        #for key in keywords.iterkeys():
        #    self.add_list_entry(key, str(keywords[key]))

        # now make the rest of the safe_qgis reflect the list entries
        #self.update_controls_from_list()


#    def read_keywords(self, layer, keyword=None):
#        """Read keywords for a datasource and return them as a dictionary.
#
#        This is a wrapper method that will 'do the right thing' to fetch
#        keywords for the given datasource. In particular, if the datasource
#        is remote (e.g. a database connection) it will fetch the keywords from
#        the keywords store.
#
#        :param layer:  A QGIS QgsMapLayer instance that you want to obtain
#            the keywords for.
#        :type layer: QgsMapLayer

#        :param keyword: If set, will extract only the specified keyword
#              from the keywords dict.
#        :type keyword: str

#        :returns: A dict if keyword is omitted, otherwise the value for the
#            given key if it is present.
#        :rtype: dict, str

#        TODO: Don't raise generic exceptions.

#        :raises: HashNotFoundError, Exception, OperationalError,
#            NoKeywordsFoundError, KeywordNotFoundError, InvalidParameterError,
#            UnsupportedProviderError

#        """
	global source
	#print source        
	#source = str(layer.source())
        #try:
        #    flag = self.are_keywords_file_based(layer)
        #except UnsupportedProviderError:
        #    raise

        #try:
            #if flag:
#        keywords = self.read_file_keywords(source)#, keyword)
	#print keywords
            #else:
                #keywords = self.read_keyword_from_uri(source, keyword)
#        return keywords
        #except (HashNotFoundError,
                #Exception,
                #OperationalError,
                #NoKeywordsFoundError,
                #KeywordNotFoundError,
                #InvalidParameterError,
                #UnsupportedProviderError):
            #raise
	

#    def are_keywords_file_based(self, layer):
#        """Check if keywords should be read/written to file or our keywords db.

#       Determine which keyword lookup system to use (file base or cache db)
#        based on the layer's provider type. True indicates we should use the
#        datasource as a file and look for a keywords file, False and we look
#        in the keywords db.

#        :param layer: The layer which want to know how the keywords are stored.
#        :type layer: QgsMapLayer

#        :returns: True if keywords are stored in a file next to the dataset,
#            else False if the dataset is remove e.g. a database.
#        :rtype: bool

#        :raises: UnsupportedProviderError
#        """

#        try:
#            provider_type = str(layer.providerType())
#        except AttributeError:
#            raise UnsupportedProviderError(
#                'Could not determine type for provider: %s' %
#                layer.__class__.__name__)

#        provider_dict = {
#            'ogr': True,
#            'gdal': True,
#            'gpx': False,
#            'wms': False,
#            'spatialite': False,
#            'delimitedtext': True,
#            'postgres': False}
#        file_based_keywords = False
#        if provider_type in provider_dict:
#            file_based_keywords = provider_dict[provider_type]
#        return file_based_keywords


#    def tr(theText):
#        myContext = "@default"
#        return QCoreApplication.translate(myContext, theText)
    def tr(theText):
      """We define a tr() alias here since the is_safe_interface implementation
      below is not a class and does not inherit from QObject.

      .. note:: see http://tinyurl.com/pyqt-differences

      Args:
         theText - string to be translated
      Returns:
         Translated version of the given string if available, otherwise
         the original string.
      """
      myContext = "@default"
      return QCoreApplication.translate(myContext, theText)


#    def read_file_keywords(self, layer_path, keyword=None):
     # check the source layer path is valid
      ##if not os.path.isfile(layer_path):
          ##message = tr('Cannot get keywords from a non-existent file.'
                       ##'%s does not exist.' % layer_path)
          ##raise InvalidParameterError(message)
      #print layer_path
#      global source
    # check there really is a keywords file for this layer
#      keyword_file_path = os.path.splitext(source)[0]
#      keyword_file_path += '.keywords'
#      if not os.path.isfile(keyword_file_path):
#          print ('No keywords file found for %s' % keyword_file_path)
#	  global no
#	  no = 0
          #raise NoKeywordsFoundError(message)
#      else:
#        global no
#        no = 1	
    # now get the requested keyword using the inasafe library
      #dictionary = None
      #try:
      #dictionary = self.read_keywords(keyword_file_path)
#        my_dict = {}
#      	with open(keyword_file_path, 'r') as f:
#    		for line in f:
#        		items = line.split()
			#print str(items[0])
			#print str(items[1:])
#        		key, values = items[0], items[1:]
#			return values        		
			#my_dict[key] = values

	#except Exception, e:
          #message = \
              #tr('Keyword retrieval failed for %s (%s) \n %s' % (
                  #keyword_file_path, keyword, str(e)))
          #raise KeywordNotFoundError(message)

    # if no keyword was supplied, just return the dict
      #if keyword is None:
          #return my_dict
      #if not keyword in my_dict:
          #message = \
              #tr('No value was found in file %s for keyword %s' % (
                  #keyword_file_path, keyword))
          #raise KeywordNotFoundError(message)

      #try:
          #value = my_dict[keyword]
      #except:
          #raise
      #print values
      #return values


#    def read_keyword_from_uri(self, uri, keyword=None):
#        """Get metadata from the keywords file associated with a URI.

#        This is used for layers that are non local layer (e.g. postgresql
#        connection) and so we need to retrieve the keywords from the sqlite
#        keywords db.

#        A hash will be constructed from the supplied uri and a lookup made
#        in a local SQLITE database for the keywords. If there is an existing
#        record it will be returned, if not and error will be thrown.

#        .. seealso:: write_keywords_for_uri, delete_keywords_for_uri

#        :param uri: A layer uri. e.g. ```dbname=\'osm\' host=localhost
#            port=5432 user=\'foo\' password=\'bar\' sslmode=disable
#            key=\'id\' srid=4326```
#        :type uri: str

#        :param keyword: The metadata keyword to retrieve. If none,
#            all keywords are returned.
#        :type keyword: str

#        :returns: A string containing the retrieved value for the keyword if
#           the keyword argument is specified, otherwise the
#           complete keywords dictionary is returned.

#        :raises: KeywordNotFoundError if the keyword is not found.
#        """
#        hash_value = self.hash_for_datasource(uri)
#        try:
#            self.open_connection()
#        except OperationalError:
#            raise
#        try:
#            cursor = self.get_cursor()
#            # now see if we have any data for our hash
#            sql = (
#                'select dict from keyword where hash = \'%s\';' % hash_value)
#            cursor.execute(sql)
#            data = cursor.fetchone()
#            # unpickle it to get our dict back
#            if data is None:
#                raise HashNotFoundError('No hash found for %s' % hash_value)
#            data = data[0]  # first field
#            picked_dict = pickle.loads(str(data))
#            if keyword is None:
#                return picked_dict
#            if keyword in picked_dict:
#                return picked_dict[keyword]
#            else:
#                raise KeywordNotFoundError('Keyword "%s" not found in %s' % (
#                    keyword, picked_dict))

#        except sqlite.Error, e:
#            LOGGER.debug("Error %s:" % e.args[0])
#        except Exception, e:
#            LOGGER.debug("Error %s:" % e.args[0])
#            raise
#        finally:
#            self.close_connection()


#    def hash_for_datasource(self, data_source):
#        """Given a data_source, return its hash.

#        :param data_source: The data_source name from a layer.
#        :type data_source: str

#        :returns: An md5 hash for the data source name.
#        :rtype: str
#        """
#        import hashlib
#        hash_value = hashlib.md5()
#        hash_value.update(data_source)
#        hash_value = hash_value.hexdigest()
#        return hash_value


#keywords files added

    def set_layer(self):
        """Set the layer associated with the keyword editor.

        :param layer: Layer whose keywords should be edited.
        :type layer: QgsMapLayer
        """
        #self.layer = layer
	self.layer = self.canvas.currentLayer()
        self.load_state_from_keywords()

    #noinspection PyMethodMayBeStatic
    def show_help(self):
        """Load the help text for the keywords dialog."""
        show_context_help(context='keywords')

    def toggle_postprocessing_widgets(self):
        """Hide or show the post processing widgets depending on context."""
        #LOGGER.debug('togglePostprocessingWidgets')
        #postprocessing_flag = self.radPostprocessing.isChecked()
        #self.cboSubcategory.setVisible(not postprocessing_flag)
        #self.lblSubcategory.setVisible(not postprocessing_flag)
        #self.show_aggregation_attribute(postprocessing_flag)
        #self.show_female_ratio_attribute(postprocessing_flag)
        #self.show_female_ratio_default(postprocessing_flag)
        #self.show_youth_ratio_attribute(postprocessing_flag)
        #self.show_youth_ratio_default(postprocessing_flag)
        #self.show_adult_ratio_attribute(postprocessing_flag)
        #self.show_adult_ratio_default(postprocessing_flag)
        #self.show_elderly_ratio_attribute(postprocessing_flag)
        #self.show_elderly_ratio_default(postprocessing_flag)


    def on_radExposure_toggled(self, theFlag):
        """Automatic slot executed when the hazard radio is toggled on.

        :param theFlag: Flag indicating the new checked state of the button.
        :type theFlag: bool
        """
        if not theFlag:
            return
        self.set_category('exposure')
        self.update_controls_from_list()

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('bool')
    def on_cboSubcategory_currentIndexChanged(self, index=None):
        """Automatic slot executed when the subcategory is changed.

        When the user changes the subcategory, we will extract the
        subcategory and dataype or unit (depending on if it is a hazard
        or exposure subcategory) from the [] after the name.

        :param index: Not used but required for Qt slot.
        """
        #if index == -1:
            #self.remove_item_by_key('subcategory')
            #return

        #text = self.dlg.ui.cboSubcategory.itemData(
            #self.dlg.ui.cboSubcategory.currentIndex())

        # I found that myText is 'Not Set' for every language
        #if text == 'Not Set' or text == 'Not Set':
            #self.remove_item_by_key('subcategory')
            #return

        #tokens = text.split(' ')
        #if len(tokens) < 1:
            #self.remove_item_by_key('subcategory')
            #return

        #subcategory = tokens[0]
        #self.add_list_entry('subcategory', subcategory)

        # Some subcategories e.g. roads have no units or datatype
        #if len(tokens) == 1:
            #return
        #if tokens[1].find('[') < 0:
            #return
        #category = self.get_value_for_key('category')
        #if 'hazard' == category:
            #units = tokens[1].replace('[', '').replace(']', '')
           # self.add_list_entry('unit', units)
        #if 'exposure' == category:
            #data_type = tokens[1].replace('[', '').replace(']', '')
            #self.add_list_entry('datatype', data_type)
            # prevents actions being handled twice

    def set_subcategory_list(self, entries, selected_item=None):
        """Helper to populate the subcategory list based on category context.

        :param entries: An OrderedDict of subcategories. The dict entries
             should be in the form ('earthquake', self.tr('earthquake')). See
             http://www.voidspace.org.uk/python/odict.html for info on
             OrderedDict.
        :type entries: OrderedDict

        :param selected_item: Which item should be selected in the combo. If
            the selected item is not in entries, it will be appended to it.
            This is optional.
        :type selected_item: str
        """
        # To avoid triggering on_cboSubcategory_currentIndexChanged
        # we block signals from the combo while updating it
        #self.dlg.ui.leSubcategory.blockSignals(True)
        ##self.dlg.ui.leSubcategory.clear()
        item_selected_flag = selected_item is not None
        selected_item_values = selected_item not in entries.values()
        selected_item_keys = selected_item not in entries.keys()
        if (item_selected_flag and selected_item_values and
                selected_item_keys):
            # Add it to the OrderedList
            entries[selected_item] = selected_item
        index = 0
        selected_index = 0
        for key, value in entries.iteritems():
            if value == selected_item or key == selected_item:
                selected_index = index
            index += 1
            #self.dlg.ui.cboSubcategory.addItem(value, key)
        #self.dlg.ui.cboSubcategory.setCurrentIndex(selected_index)
        #self.dlg.ui.cboSubcategory.blockSignals(False)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnAddToList1_clicked(self):
        """Automatic slot executed when the pbnAddToList1 button is pressed.
        """
        if (self.lePredefinedValue.text() != "" and
                self.cboKeyword.currentText() != ""):
            current_key = self.cboKeyword.currentText()
            current_value = self.lePredefinedValue.text()
            self.add_list_entry(current_key, current_value)
            self.lePredefinedValue.setText('')
            self.update_controls_from_list()

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnAddToList2_clicked(self):
        """Automatic slot executed when the pbnAddToList2 button is pressed.
        """

        current_key = self.leKey.text()
        current_value = self.leValue.text()
        if current_key == 'category' and current_value == 'hazard':
            ##self.dlg.ui.radHazard.blockSignals(True)
            ##self.dlg.ui.radHazard.setChecked(True)
            self.set_subcategory_list(self.standard_hazard_list)
            ##self.dlg.ui.radHazard.blockSignals(False)
        elif current_key == 'category' and current_value == 'exposure':
            ##self.dlg.ui.radExposure.blockSignals(True)
            ##self.dlg.ui.radExposure.setChecked(True)
            self.set_subcategory_list(self.standard_exposure_list)
            ##self.dlg.ui.radExposure.blockSignals(False)
        elif current_key == 'category':
            #.. todo:: notify the user their category is invalid
            pass
        self.add_list_entry(current_key, current_value)
        self.leKey.setText('')
        self.leValue.setText('')
        self.update_controls_from_list()

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_pbnRemove_clicked(self):
        """Automatic slot executed when the pbnRemove button is pressed.

        Any selected items in the keywords list will be removed.
        """
        for item in self.lstKeywords.selectedItems():
            self.lstKeywords.takeItem(self.lstKeywords.row(item))
        self.leKey.setText('')
        self.leValue.setText('')
        self.update_controls_from_list()

    def add_list_entry(self, key, value):
        """Add an item to the keywords list given its key/value.

        The key and value must both be valid, non empty strings
        or an InvalidKVPError will be raised.

        If an entry with the same key exists, it's value will be
        replaced with value.

        It will add the current key/value pair to the list if it is not
        already present. The kvp will also be stored in the data of the
        listwidgetitem as a simple string delimited with a bar ('|').

        :param key: The key part of the key value pair (kvp).
        :type key: str

        :param value: Value part of the key value pair (kvp).
        :type value: str
        """
        if key is None or key == '':
            return
        if value is None or value == '':
            return

        # make sure that both key and value is string
        key = key
        value = value
        message = ''
        if ':' in key:
            key = key.replace(':', '.')
            message = 'Colons are not allowed, replaced with "."'
        if ':' in value:
            value = value.replace(':', '.')
            message = 'Colons are not allowed, replaced with "."'
        #if message == '':
            #self.lblMessage.setText('')
            #self.lblMessage.hide()
        #else:
            #self.lblMessage.setText(message)
            #self.lblMessage.show()
        item = QtGui.QListWidgetItem(key + ':' + value)
        # We are going to replace, so remove it if it exists already
        #self.remove_item_by_key(key)
        data = key + '|' + value
        item.setData(QtCore.Qt.UserRole, data)
        #self.lstKeywords.insertItem(0, item)

    def set_category(self, category):
        """Set the category radio button based on category.

        :param category: Either 'hazard', 'exposure' or 'postprocessing'.
        :type category: str

        :returns: False if radio button could not be updated, otherwise True.
        :rtype: bool
        """
        # convert from QString if needed
        category = str(category)
#        if self.get_value_for_key('category') == category:
            #nothing to do, go home
#            return True
        if category not in ['hazard', 'exposure', 'postprocessing']:
            # .. todo:: report an error to the user
            return False
            # Special case when category changes, we start on a new slate!

        if category == 'hazard':
            # only cause a toggle if we actually changed the category
            # This will only really be apparent if user manually enters
            # category as a keyword
            self.reset()
            ##self.dlg.ui.radHazard.blockSignals(True)
            ##self.dlg.ui.radHazard.setChecked(True)
            ##self.dlg.ui.radHazard.blockSignals(False)
            #self.remove_item_by_key('subcategory')
            #self.remove_item_by_key('datatype')
            self.add_list_entry('category', 'hazard')
            hazard_list = self.standard_hazard_list
            self.set_subcategory_list(hazard_list)

        elif category == 'exposure':
            self.reset()
            ##self.dlg.ui.radExposure.blockSignals(True)
            ##self.dlg.ui.radExposure.setChecked(True)
            ##self.dlg.ui.radExposure.blockSignals(False)
            #self.remove_item_by_key('subcategory')
            #self.remove_item_by_key('unit')
            self.add_list_entry('category', 'exposure')
            exposure_list = self.standard_exposure_list
            self.set_subcategory_list(exposure_list)

        else:
            self.reset()
            self.radPostprocessing.blockSignals(True)
            self.radPostprocessing.setChecked(True)
            self.radPostprocessing.blockSignals(False)
            #self.remove_item_by_key('subcategory')
            self.add_list_entry('category', 'postprocessing')

        return True

    def reset(self, primary_keywords_only=True):
        """Reset all controls to a blank state.

        :param primary_keywords_only: If True (the default), only reset
            Subcategory, datatype and units.
        :type primary_keywords_only: bool
        """

        ##self.dlg.ui.leSubcategory.clear()
        #self.remove_item_by_key('subcategory')
        #self.remove_item_by_key('datatype')
        #self.remove_item_by_key('unit')
        #self.remove_item_by_key('source')
        #if not primary_keywords_only:
            # Clear everything else too
            #self.lstKeywords.clear()
        #self.leKey.clear()
        #self.leValue.clear()
        #self.lePredefinedValue.clear()
        ##self.dlg.ui.leTitle.clear()
        ##self.dlg.ui.leSource.clear()
	##self.dlg.ui.radExposure.setChecked(True)
	##self.dlg.ui.lblLayerName.clear()
	#self.set_layer()

#    def remove_item_by_key(self, removal_key):
#        """Remove an item from the kvp list given its key.

#        :param removal_key: Key of item to be removed.
#        :type removal_key: str
#        """
#        for myCounter in range(self.lstKeywords.count()):
#            existing_item = self.lstKeywords.item(myCounter)
#            text = existing_item.text()
#            tokens = text.split(':')
#            if len(tokens) < 2:
#                break
#            key = tokens[0]
#            if removal_key == key:
#                # remove it since the removal_key is already present
#                self.lstKeywords.takeItem(myCounter)
#                break

#    def remove_item_by_value(self, removal_value):
#        """Remove an item from the kvp list given its key.
#
#        :param removal_value: Value of item to be removed.
#        :type removal_value: str
#        """
#        for counter in range(self.lstKeywords.count()):
#            existing_item = self.lstKeywords.item(counter)
#            text = existing_item.text()
#            tokens = text.split(':')
#            value = tokens[1]
#            if removal_value == value:
#                # remove it since the key is already present
#                self.lstKeywords.takeItem(counter)
#                break

#    def get_value_for_key(self, lookup_key):
#        """If key list contains a specific key, return its value.

#        :param lookup_key: The key to search for
#        :type lookup_key: str

#        :returns: Value of key if matched otherwise none.
#        :rtype: str
#        """
#        for counter in range(self.lstKeywords.count()):
#            existing_item = self.lstKeywords.item(counter)
#            text = existing_item.text()
#            tokens = text.split(':')
#            key = str(tokens[0]).strip()
#            value = str(tokens[1]).strip()
#            if lookup_key == key:
#                return value
#        return None

    def load_state_from_keywords(self):
        """Set the ui state to match the keywords of the active layer.

        In case the layer has no keywords or any problem occurs reading them,
        start with a blank slate so that subcategory gets populated nicely &
        we will assume exposure to start with.

        Also if only title is set we use similar logic (title is added by
        default in dock and other defaults need to be explicitly added
        when opening this dialog). See #751

        """
        keywords = {'category': 'exposure'}

        try:
            # Now read the layer with sub layer if needed
            keywords = self.keyword_io.read_keywords(self.layer)
        except (InvalidParameterError,
                HashNotFoundError):
                #NoKeywordsFoundError):
            pass

        layer_name = self.layer.name()
        #if 'title' not in keywords:
        ##self.dlg.ui.leTitle.setText(self.layer.name())
	#print self.layer.name()
        ##self.dlg.ui.lblLayerName.setText('Keywords for %s' % self.layer.name())

        ##if 'source' in keywords:
	    #print str(keywords['source'])
            ##self.dlg.ui.leSource.setText(str(keywords['source']))
        ##else:
	    #print "come"
            ##self.dlg.ui.leSource.setText('')

        # if we have a category key, unpack it first
        # so radio button etc get set
        if 'category' in keywords:
            self.set_category(keywords['category'])
            keywords.pop('category')
        else:
            # assume exposure to match ui. See issue #751
            self.add_list_entry('category', 'exposure')

        for key in keywords.iterkeys():
            self.add_list_entry(key, str(keywords[key]))

	if 'subcategory' in keywords:
            self.set_category(keywords['subcategory'])
	    ##self.dlg.ui.leSubcategory.setText(keywords['subcategory'])
	
	if str(keywords['subcategory']) == 'flood':
	    #print "come1"
	    global layer_path_haz
	    global floodLyrForRpt
	    layer_path_haz = str(self.layer.source())
	    floodLyrForRpt = str(self.layer.name())
	    #print layer_path_haz

	elif str(keywords['subcategory']) == 'road':
            #print "come2"
	    global layer_path_rd
	    layer_path_rd = str(self.layer.source())
	    ##global roadLayer
	    ##roadLayer = str(self.layer.name())
            #print layer_path_rd	

	#print layer_path_haz
	#print layer_path_rd
        # now make the rest of the safe_qgis reflect the list entries
        self.update_controls_from_list()

    def update_controls_from_list(self):
        """Set the ui state to match the keywords of the active layer."""
        #subcategory = self.get_value_for_key('subcategory')
        #units = self.get_value_for_key('unit')
        #data_type = self.get_value_for_key('datatype')
        #title = self.get_value_for_key('title')
        #if title is not None:
        #self.dlg.ui.leTitle.setText(title)
        if self.layer is not None:
            layer_name = self.layer.name()
	    ##self.dlg.ui.leTitle.setText(self.layer.name())
            ##self.dlg.ui.lblLayerName.setText('Keywords for %s' % layer_name)
        else:
            ##self.dlg.ui.lblLayerName.setText('')
	    print 'hi'
        #if not is_polygon_layer(self.layer):
            #self.radPostprocessing.setEnabled(False)

        # adapt gui if we are in postprocessing category
        self.toggle_postprocessing_widgets()

        #if self.dlg.ui.radExposure.isChecked():
        #    if subcategory is not None and data_type is not None:
        #        self.set_subcategory_list(
        #            self.standard_exposure_list,
        #            subcategory + ' [' + data_type + ']')
        #    elif subcategory is not None:
        #        self.set_subcategory_list(
        #            self.standard_exposure_list, subcategory)
        #    else:
        #        self.set_subcategory_list(
        #            self.standard_exposure_list,
        #            'Not Set')
        #elif self.dlg.ui.radHazard.isChecked():
            #if subcategory is not None and units is not None:
                #self.set_subcategory_list(
                    #self.standard_hazard_list,
                    #subcategory + ' [' + units + ']')
            #elif subcategory is not None:
                #self.set_subcategory_list(
                    #self.standard_hazard_list,
                    #subcategory)
            #else:
                #self.set_subcategory_list(
                    #self.standard_hazard_list,
                    #'Not Set')

        self.resize_dialog()

    def resize_dialog(self):
        """Resize the dialog to fit its contents."""
        # noinspection PyArgumentList
        QtCore.QCoreApplication.processEvents()
        #LOGGER.debug('adjust ing dialog size')
        #self.adjustSize()

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('QString')
    def on_leTitle_textEdited(self, title):
        """Update the keywords list whenever the user changes the title.

        This slot is not called if the title is changed programmatically.

        :param title: New title keyword for the layer.
        :type title: str
        """
        self.add_list_entry('title', str(title))

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('QString')
    def on_leSource_textEdited(self, source):
        """Update the keywords list whenever the user changes the source.

        This slot is not called if the source is changed programmatically.

        :param source: New source keyword for the layer.
        :type source: str
        """
        if source is None or source == '':
            self.remove_item_by_key('source')
        else:
            self.add_list_entry('source', str(source))

    def get_keywords(self):
        """Obtain the state of the dialog as a keywords dict.

        :returns: Keywords reflecting the state of the dialog.
        :rtype: dict
        """
        #make sure title is listed
        ##if str(self.dlg.ui.leTitle.text()) != '':
            ##self.add_list_entry('title', str(self.dlg.ui.leTitle.text()))

        # make sure the source is listed too
        ##if str(self.dlg.ui.leSource.text()) != '':
            ##self.add_list_entry('source', str(self.dlg.ui.leSource.text()))

        keywords = {}
        for myCounter in range(self.lstKeywords.count()):
            existing_item = self.lstKeywords.item(myCounter)
            text = existing_item.text()
            tokens = text.split(':')
            key = str(tokens[0]).strip()
            value = str(tokens[1]).strip()
            keywords[key] = value
        return keywords

    def accept(self):
        """Automatic slot executed when the ok button is pressed.

        It will write out the keywords for the layer that is active.
        """
        self.apply_changes()
        keywords = self.get_keywords()
        try:
            self.keyword_io.write_keywords(
                layer=self.layer, keywords=keywords)
        except InaSAFEError, e:
            error_message = get_error_message(e)
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QtGui.QMessageBox.warning(
                self, 'InaSAFE',
                ((
                    'An error was encountered when saving the keywords:\n'
                    '%s' % error_message.to_html())))
        if self.dock is not None:
            self.dock.get_layers()
        self.done(QtGui.QDialog.Accepted)

    def apply_changes(self):
        """Apply any pending changes e.g. keywords entered without being added.

        See https://github.com/AIFDR/inasafe/issues/249
        """

        if self.radPredefined.isChecked():
            self.on_pbnAddToList1_clicked()
        else:
            self.on_pbnAddToList2_clicked()

    def edit_key_value_pair(self, item):
        """Slot to set leKey and leValue to clicked item in the lstKeywords.

        :param item: A Key Value pair expressed as a string where the first
            colon in the string delimits the key from the value.
        :type item: QListWidgetItem
        """
        temp_key = item.text().split(':')[0]
        temp_value = item.text().split(':')[1]
        if temp_key == 'category':
            return
        if self.radUserDefined.isChecked():
            self.leKey.setText(temp_key)
            self.leValue.setText(temp_value)
        elif self.radPredefined.isChecked():
            index_key = self.cboKeyword.findText(temp_key)
            if index_key > -1:
                self.cboKeyword.setCurrentIndex(index_key)
                self.lePredefinedValue.setText(temp_value)
            else:
                self.radUserDefined.setChecked(True)
                self.leKey.setText(temp_key)
                self.leValue.setText(temp_value)



    def refresh(self):
	self.set_layer()



	##*************************************************keywords

    def clearFields(self):
	self.dlg.clearTextBrowserStart()
	self.dlg.clearTextBrowserStop()
	self.dlg.clearTextBrowserDesStart()
	self.dlg.clearTextBrowserDesStop()
        cLayer = self.canvas.currentLayer()
	cLayer.removeSelection()
	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownStart)
	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownStop)
        QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeatureStart)	
        QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeatureStop)
	#QObject.disconnect(self.dlg.ui.btnFindRoutesR,SIGNAL("clicked()"),self.findRoutes)

	self.dlg.ui.cmbHospitalLayerR.clear()
	self.dlg.ui.cmbIDPCampLayerR.clear()
	self.dlg.ui.cmbHospitalR.clear()
	self.dlg.ui.cmbIDPCampR.clear()
	self.dlg.ui.cmbHospitalLayerR.addItem('Select layer')
	self.dlg.ui.cmbIDPCampLayerR.addItem('Select layer')
	self.dlg.ui.cmbHospitalR.addItem('Select Hospital')
	self.dlg.ui.cmbIDPCampR.addItem('Select IDP Camp')
	#global rH
	#rH = 1
	#global rI
	#rI = 1

	allLayersLoaded = self.canvas.layers()
 	for SelLayer in allLayersLoaded:	
		self.dlg.ui.cmbHospitalLayerR.addItem(SelLayer.name())
		self.dlg.ui.cmbIDPCampLayerR.addItem(SelLayer.name())

	self.dlg.ui.cmbHospitalLayerR.setCurrentIndex(0)
	self.dlg.ui.cmbIDPCampLayerR.setCurrentIndex(0)
	self.dlg.ui.cmbHospitalR.setCurrentIndex(0)
	self.dlg.ui.cmbIDPCampR.setCurrentIndex(0)
	self.dlg.ui.btnDirectionstxt.setVisible(False)
	self.dlg.ui.btnDirectionsImage.setVisible(False)
	self.dlg.ui.btnDirectionsPDF.setVisible(False)
	self.dlg.ui.btnDirectionsAudio.setVisible(False)
	self.dlg.ui.lblGenerateDirecFiles.setVisible(False)
	self.dlg.ui.btnshowDetailsHos.setVisible(False)
	self.dlg.ui.btnshowDetailsIDP.setVisible(False)	

	try:
		self.dlg.ui.lblWarnRoad.setVisible(False)
		self.dlg.ui.lblNoIDPReach.setVisible(False)
		self.dlg.ui.lblNoHospReach.setVisible(False)
		self.dlg.ui.lblWait.setVisible(False)		
		#test
		#global mm
		#self.canvas.scene().removeItem(mm)
		self.labelDirPlc.setVisible(False)
		global m1
		self.canvas.scene().removeItem(m1)
		global m2
		self.canvas.scene().removeItem(m2)
		global rb
		self.canvas.scene().removeItem(rb)
		#global vl
		#palyr = QgsPalLayerSettings()
		#palyr.readFromLayer(vl)
		#palyr.enabled = False
		#palyr.fieldName = 'name'
		#palyr.placement = QgsPalLayerSettings.OverPoint
		#palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'10','')
		# palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
		#palyr.writeToLayer(vl)
		#self.canvas.refresh()
		#deactive temp layer
		global tempLayer
		legendd = self.iface.legendInterface()
		allLayersListNeww = self.canvas.layers()
 		for getLayerNeww in allLayersListNeww:
			if str(getLayerNeww.name()) == str(tempLayer):
				legendd.setLayerVisible(getLayerNeww, False)

		#global vll
		#palyrr = QgsPalLayerSettings()
		#palyrr.readFromLayer(vll)
		#palyrr.enabled = False
		#palyrr.fieldName = 'name'
		#palyrr.placement = QgsPalLayerSettings.OverPoint
		#palyrr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
		# palyr.setDataDefinedProperty(QgsPalLayerSettings.Color,True,True,'red','')
		#palyrr.writeToLayer(vll)
		#self.canvas.refresh()
		#global rbb
		#self.canvas.scene().removeItem(rbb)
		#global mm
		#self.canvas.scene().removeItem(mm)	
		#global r
		#self.canvas.scene().removeItem(r)
		global stopPlace
		stopPlace == 1
		self.labelPos.clear()
	except:
		e = sys.exc_info()[0]
	#print e
		
	
    def saveAs(self):
	##self.iface.mapCanvas().saveAsImage('/home/kasun/testData.png', None, 'PNG')
	#QMessageBox.information( self.iface.mainWindow(),"Info", "Map Canvas saved successfully" )

##not working
	mapRenderer = self.canvas.mapRenderer()
	c = QgsComposition(mapRenderer)
	c.setPlotStyle(QgsComposition.Print)
	dpi = c.printResolution()
	dpmm = dpi / 25.4
	width = int(dpmm * c.paperWidth())
	height = int(dpmm * c.paperHeight())
	# create output image and initialize it
	image = QImage(QSize(width, height), QImage.Format_ARGB32)
	image.setDotsPerMeterX(dpmm * 1000)
	image.setDotsPerMeterY(dpmm * 1000)
	image.fill(0)
	# render the composition
	imagePainter = QPainter(image)
	sourceArea = QRectF(0, 0, c.paperWidth(), c.paperHeight())
	targetArea = QRectF(0, 0, width, height)
	c.render(imagePainter, targetArea, sourceArea)
	imagePainter.end()
	image.save("/home/kasun/out.png", "png")
	##QMessageBox.information( self.iface.mainWindow(),"Info", "Map Canvas saved successfully" )
##not working

	##pdf
#	printer = QPrinter()
#	printer.setOutputFormat(QPrinter.PdfFormat)
#	printer.setOutputFileName("/home/kasun/output.pdf")
#	printer.setPaperSize(QSizeF(c.paperWidth(), c.paperHeight()), QPrinter.Millimeter)
#	printer.setFullPage(True)
#	printer.setColorMode(QPrinter.Color)
#	printer.setResolution(c.printResolution())
#	pdfPainter = QPainter(printer)
#	paperRectMM = printer.pageRect(QPrinter.Millimeter)
#	paperRectPixel = printer.pageRect(QPrinter.DevicePixel)
#	c.render(pdfPainter, paperRectPixel, paperRectMM)
#	pdfPainter.end()


	#messagebox
	colBl = '<font color="blue">'
	colBls = '</font>'	
	textToShow = "Make sure that map canvas is zoomed to the desired zoom level"
	textSub = "The image will be saved in " + colBl + "/home " + colBls + "directory"
	textLoc = colBl + "/home/kasun/output_canvas.png " + colBls
	msgBox = QtGui.QMessageBox()
 	msgBox.setText(str(textToShow))
 	msgBox.setInformativeText(str(textSub))
 	msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
	msgBox.setDefaultButton(QMessageBox.Save)
	msgBox.setWindowTitle("Save as image")
 	ret = msgBox.exec_();

	if (ret == msgBox.Save):
		#print "Save"
		#self.iface.actionZoomToSelected().trigger()
		self.canvas.saveAsImage('/home/kasun/output_canvas.png', None, 'PNG')
		QMessageBox.information( self.iface.mainWindow(),"Info", "Map Canvas saved successfully" )
		#QMessageBox.setInformativeText(str(textLoc))
	elif (ret == msgBox.Discard):
		print "Discard"
	elif (ret == msgBox.Cancel):
		print "Cancel"
	else:
		print "None"	
	#messagebox

    def generateReportFindRoute(self):
	style = getSampleStyleSheet()
	#global repID
	#repID = repID + 1
	#repNm = "Alternative Route Finder-FLOOgin Report" + str(repID) + ".pdf"
	global filePath	
	pdf = SimpleDocTemplate("Alternative Route Finder-Find Route.pdf")
	story = []
	details = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h1>'
	#Heads = pdf.beginText(inch * 2, inch * 11)
	details.append( h2 + clR + "<b>Alternative Route Finder - Find Route </b>" + clRs + h2s )
	#details.append(Spacer(inch * .5, inch * .5))
	#pdf.drawText(Heads)
	#Details = pdf.beginText(inch * 1, inch * 10)
	global floodLyrForRpt 
	global startNameForReport
	global stopNameForReport
	global x1
	global y1
	global x2
	global y2
	global ds
	global direcForReport
	global direcForReportSimple
	global angCount
	global simpleCount
	global mode
	global hrs
	global minutes
	global dKmH
	global bRoadsForReport
	global bRoadsfCount
	global bRoadsSum
	global bRoadsCatForReport
	global bRoadsCatSpeciForReport
	global provSelected
	global distSelected
	global dsSelected
	global gndSelected

	crs = str(self.iface.activeLayer().crs().authid())

	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")
	time = now.strftime("%H:%M")

	detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " + clBl + str(floodLyrForRpt) + clBls
	detDateTime = "Generated on : " + date + " at " + time
	detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates" 
	detFindRoute = clBl + "<b>Find Route</b> " + clBls
	detFrom = clBl + "From :- " + clBls + str(startNameForReport)
	detFromCo = clBl + "Coordinates :- X : " + clBls + str(x1) + ", " + clBl + "Y : " + clBls + str(y1)  	
	detTo = clBl + "To :- " + clBls + str(stopNameForReport)
	detToCo = clBl + "Coordinates :- X : " + clBls + str(x2) + ", " + clBl + "Y : " + clBls + str(y2)
	detDis = clBl + "Distance in km : " + clBls + str(ds) + clBl + " km " + clBls
	dsMile = ds * 0.621371 	
	#met = ds * 1000
	detDism = clBl + "Distance in miles : " + clBls + str(dsMile) + clBl + " miles " + clBls
	#detImage = clBl + "<b>Map Canvas preview</b> " + clBls
	detModeTrans = clBl + "Mode of transport selected : " + clBls + str(mode)
	dMilesH = dKmH * 0.621371
	detSpeed = clBl + "Speed of travel selected : " + clBls + str(dKmH) + " km/h , " + str(dMilesH) + " mph "
	detTime = clBl + "Average time to travel : " + clBls + str(hrs) + " hour(s) and " + str(minutes) + " mins "   	
	detDirec = clBl + "<b>Directions</b> " + clBls
	##detBlockedRds = clBl + "<b>Details of Blocked Roads</b> " + clBls
	##detBRoadsSum = clBl + "<b>Summary Table - Blocked Roads Count</b> " + clBls
	##detBlockedRdsCat = clBl + "<b>Details of Blocked Roads with Administrative Divisions</b> " + clBls
	##detBlockedRdsSpeci = clBl + "<b>Details of Blocked Roads for Selected Administrative Divisions</b> " + clBls
	##detProvDis = "<b>Blocked Roads in</b> " + str(gndSelected) + " Grama Niladhari Administration Division of " + str(dsSelected) + " Divisional Secretariat, " + str(distSelected) + " District, " + str(provSelected) + " Province"
		
	#para1 = Paragraph(detFrom, style["Normal"])
	#para2 = Paragraph(detFromCo, style["Normal"])
	details.append(str(detHazard))
	details.append(str(detDateTime))
	details.append(str(detCrs))
	details.append(str(detFindRoute))	
	details.append(str(detFrom))
	#details.append("\n")
	details.append(str(detFromCo))
	#story.append(Spacer(inch * .5, inch * .5))
	#details.append("\n")
	#details.append("\n")	
	details.append(str(detTo))
	#details.append("\n")
	details.append(str(detToCo))
	#story.append(Spacer(inch * .5, inch * .5))
	#details.append("\n")
	#details.append("\n")	
	details.append(str(detDis))
	#details.append("\n")
	details.append(str(detDism))
	#story.append(Spacer(inch * .5, inch * .5))
	#details.append("\n")
	#details.append("\n")
	#details.append(str(detImage))
	details.append(str(detModeTrans))
	details.append(str(detSpeed))
	details.append(str(detTime))
	details.append(str(detDirec))	
	#story.append(Spacer(inch * .5, inch * .5))
	#details.append("\n")
	#details.append("\n")
	#story.append(Details)
	#text = "kasun ramanayake"
	##tbRoads=Table(bRoadsForReport)#, colWidths=[pdf.width/4.0]*2)
	##tbRoadsSum = Table(bRoadsSum, colWidths=[pdf.width/3.0])
	##tbRoadsCat = Table(bRoadsCatForReport)
	##tbRoadsSpeci = Table(bRoadsCatSpeciForReport)
	l = 0
	while l < simpleCount:
		#text = str(direcForReport[l])
		#para = Paragraph(text, style["Normal"])
		# details.append(str(direcForReport[l]))
		details.append(str(direcForReportSimple[l]))
		#details.append("\n")
		#story.append(Spacer(inch * .5, inch * .5))		
		#pdf.drawText(Details)
		#Details.textLine(" ")		
		l = l + 1
	#for x in xrange(25):
      		#para = Paragraph(text, style["Normal"])
      		#story.append(para)
      		#story.append(Spacer(inch * .5, inch * .5))
	#details.append([Image("testData.png")])
	#self.iface.mapCanvas().saveAsImage('/home/kasun/output_canvas.png', None, 'PNG')
	##details.append(str(detBlockedRds))
	##details.append(str(detBRoadsSum))	
	##details.append(str(detBlockedRdsCat))
	##details.append(str(detBlockedRdsSpeci))
	##details.append(str(detProvDis))	
	
	##e = 0
	##while e < bRoadsfCount:
		##details.append(str(bRoadsForReport[e]))
		##e = e + 1
	
	#details.append( t )	
	a = 0
	coun = simpleCount + 15
	##coun = 9
	while a < coun:
		text = str(details[a])
		if a == 0:
			story.append(Image("logo.png", 2*inch, 1*inch))
			story.append(Image("mottoo.png", 4*inch, 0.5*inch))
		if a == 0 or a == 4 or a == 14: ##or a == simpleCount + 15: #or a == simpleCount + 16 or a == simpleCount + 17:
			para = Paragraph(text, style['Heading2'])
		else:
			para = Paragraph(text, style["Normal"])
		story.append(para)
		story.append(Spacer(inch * .2, inch * .2))
		a = a + 1
		##if a == simpleCount + 16:
			##story.append( tbRoads )
			##story.append(Spacer(inch * .2, inch * .2))
		##if a == simpleCount + 17:
			##story.append( tbRoadsSum )
			##story.append(Spacer(inch * .2, inch * .2))
		##if a == simpleCount + 18:
			##story.append( tbRoadsCat )
			##story.append(Spacer(inch * .2, inch * .2))
		if a == 5:
			story.append(Image("FLOOgin_path.png", 6*inch, 3.5*inch))
			story.append(Spacer(inch * .2, inch * .2))
		if a == simpleCount + 15:
			##story.append( tbRoadsSpeci )
			##story.append(Spacer(inch * .2, inch * .2))
			story.append(Image("end1.png", 6*inch, 0.5*inch))
				
	#pdf.showPage()
 	#pdf.save()
	#pdf.build([Image("testData.png")])
	#story.append(Image("/home/kasun/output_canvas.png", 6*inch, 4*inch))
	pdf.build(story, canvasmaker=NumberedCanvas)
	#copy file to relevant directory
	src = 'Alternative Route Finder-Find Route.pdf'
	dst = str(filePath)
	self.copyFile(src,dst)
	webbrowser.open('Alternative Route Finder-Find Route.pdf')



    def generateReport(self):
	self.genBRoadsImage()
	style = getSampleStyleSheet()
	#global repID
	#repID = repID + 1
	#repNm = "Alternative Route Finder-FLOOgin Report" + str(repID) + ".pdf"	
	pdf = SimpleDocTemplate("Alternative Route Finder-FLOOgin Report.pdf")
	story = []
	details = []
	clBl = '<font color="blue">'
	clBls = '</font>'
	clR = '<font color="red">'
	clRs = '</font>'
	h2 = '<h1>'
	h2s = '</h1>'
	#Heads = pdf.beginText(inch * 2, inch * 11)
	details.append( h2 + clR + "<b>Alternative Route Finder - FLOOgin Report </b>" + clRs + h2s )
	#details.append(Spacer(inch * .5, inch * .5))
	#pdf.drawText(Heads)
	#Details = pdf.beginText(inch * 1, inch * 10)
	global floodLyrForRpt 
	global startNameForReport
	global stopNameForReport
	global x1
	global y1
	global x2
	global y2
	global ds
	global direcForReport
	global direcForReportSimple
	global angCount
	global simpleCount
	global mode
	global hrs
	global minutes
	global dKmH
	global bRoadsForReport
	global bRoadsfCount
	global bRoadsSum
	global bRoadsCatForReport
	global bRoadsCatSpeciForReport
	global provSelected
	global distSelected
	global dsSelected
	global gndSelected

	crs = str(self.iface.activeLayer().crs().authid())

	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")
	time = now.strftime("%H:%M")

	detHazard = "The Report is based on the Flood Hazard Event sourced by Hazard shapefile " + clBl + str(floodLyrForRpt) + clBls
	detDateTime = "Generated on : " + date + " at " + time
	detCrs = "Coordinate Reference System : " + str(crs) + " geographic coordinates" 
	##detFindRoute = clBl + "<b>Find Route</b> " + clBls
	##detFrom = clBl + "From :- " + clBls + str(startNameForReport)
	##detFromCo = clBl + "Coordinates :- X : " + clBls + str(x1) + ", " + clBl + "Y : " + clBls + str(y1)  	
	##detTo = clBl + "To :- " + clBls + str(stopNameForReport)
	##detToCo = clBl + "Coordinates :- X : " + clBls + str(x2) + ", " + clBl + "Y : " + clBls + str(y2)
	##detDis = clBl + "Distance in km : " + clBls + str(ds) + clBl + " km " + clBls
	##dsMile = ds * 0.621371 	
	#met = ds * 1000
	##detDism = clBl + "Distance in miles : " + clBls + str(dsMile) + clBl + " miles " + clBls
	#detImage = clBl + "<b>Map Canvas preview</b> " + clBls
	##detModeTrans = clBl + "Mode of transport selected : " + clBls + str(mode)
	##dMilesH = dKmH * 0.621371
	##detSpeed = clBl + "Speed of travel selected : " + clBls + str(dKmH) + " km/h , " + str(dMilesH) + " mph "
	##detTime = clBl + "Average time to travel : " + clBls + str(hrs) + " hour(s) and " + str(minutes) + " mins "   	
	##detDirec = clBl + "<b>Directions</b> " + clBls
	detBlockedRds = clBl + "<b>Details of Blocked Roads</b> " + clBls
	detBRoadsSum = clBl + "<b>Summary Table - Blocked Roads Count</b> " + clBls
	detBlockedRdsCat = clBl + "<b>Details of Blocked Roads with Administrative Divisions</b> " + clBls
	detBlockedRdsSpeci = clBl + "<b>Details of Blocked Roads for Selected Administrative Divisions</b> " + clBls
	detProvDis = "<b>Blocked Roads in</b> " + str(gndSelected) + " Grama Niladhari Administration Division of " + str(dsSelected) + " Divisional Secretariat, " + str(distSelected) + " District, " + str(provSelected) + " Province"
		
	#para1 = Paragraph(detFrom, style["Normal"])
	#para2 = Paragraph(detFromCo, style["Normal"])
	details.append(str(detHazard))
	details.append(str(detDateTime))
	details.append(str(detCrs))
	##details.append(str(detFindRoute))	
	##details.append(str(detFrom))
	#details.append("\n")
	##details.append(str(detFromCo))
	#story.append(Spacer(inch * .5, inch * .5))
	#details.append("\n")
	#details.append("\n")	
	##details.append(str(detTo))
	#details.append("\n")
	##details.append(str(detToCo))
	#story.append(Spacer(inch * .5, inch * .5))
	#details.append("\n")
	#details.append("\n")	
	##details.append(str(detDis))
	#details.append("\n")
	##details.append(str(detDism))
	#story.append(Spacer(inch * .5, inch * .5))
	#details.append("\n")
	#details.append("\n")
	#details.append(str(detImage))
	##details.append(str(detModeTrans))
	##details.append(str(detSpeed))
	##details.append(str(detTime))
	##details.append(str(detDirec))	
	#story.append(Spacer(inch * .5, inch * .5))
	#details.append("\n")
	#details.append("\n")
	#story.append(Details)
	#text = "kasun ramanayake"
	tbRoads=Table(bRoadsForReport)#, colWidths=[pdf.width/4.0]*2)
	tbRoadsSum = Table(bRoadsSum, colWidths=[pdf.width/3.0])
	tbRoadsCat = Table(bRoadsCatForReport)
	tbRoadsSpeci = Table(bRoadsCatSpeciForReport)
	##l = 0
	##while l < simpleCount:
		#text = str(direcForReport[l])
		#para = Paragraph(text, style["Normal"])
		# details.append(str(direcForReport[l]))
		##details.append(str(direcForReportSimple[l]))
		#details.append("\n")
		#story.append(Spacer(inch * .5, inch * .5))		
		#pdf.drawText(Details)
		#Details.textLine(" ")		
		##l = l + 1
	#for x in xrange(25):
      		#para = Paragraph(text, style["Normal"])
      		#story.append(para)
      		#story.append(Spacer(inch * .5, inch * .5))
	#details.append([Image("testData.png")])
	#self.iface.mapCanvas().saveAsImage('/home/kasun/output_canvas.png', None, 'PNG')
	details.append(str(detBlockedRds))
	details.append(str(detBRoadsSum))	
	details.append(str(detBlockedRdsCat))
	details.append(str(detBlockedRdsSpeci))
	details.append(str(detProvDis))	
	
	##e = 0
	##while e < bRoadsfCount:
		##details.append(str(bRoadsForReport[e]))
		##e = e + 1
	
	#details.append( t )	
	a = 0
	##coun = simpleCount + 20
	coun = 9
	while a < coun:
		text = str(details[a])
		if a == 0:
			story.append(Image("logo.png", 2*inch, 1*inch))
			story.append(Image("mottoo.png", 4*inch, 0.5*inch))
		if a == 0 or a == 4: ##or a == 14 or a == simpleCount + 15: #or a == simpleCount + 16 or a == simpleCount + 17:
			para = Paragraph(text, style['Heading2'])
		else:
			para = Paragraph(text, style["Normal"])
		story.append(para)
		story.append(Spacer(inch * .2, inch * .2))
		a = a + 1
		##if a == simpleCount + 16:
		if a == 5:
			story.append( tbRoads )
			story.append(Spacer(inch * .2, inch * .2))
		##if a == simpleCount + 17:
		if a == 6:
			story.append( tbRoadsSum )
			story.append(Spacer(inch * .2, inch * .2))
		##if a == simpleCount + 18:
		if a == 7:
			story.append( tbRoadsCat )
			story.append(Spacer(inch * .2, inch * .2))
		##if a == simpleCount + 20:
		if a == 9:
			story.append( tbRoadsSpeci )
			story.append(Spacer(inch * .2, inch * .2))
			#story.append(Image("end1.png", 6*inch, 0.5*inch))
				
	#pdf.showPage()
 	#pdf.save()
	#pdf.build([Image("testData.png")])
	#story.append(Image("/home/kasun/output_canvas.png", 6*inch, 4*inch))
	pdf.build(story, canvasmaker=NumberedCanvas)
	##pdf.build(story)
	#pdf.build([Image("testData.png")])
	# messagebox
	#colBl = '<font color="blue">'
	#colBls = '</font>'	
	#textToShow = "Report generated successfully"
	#textSub = "Saved in " + colBl + "/home " + colBls + "directory, " + '\n' + " Name of report : Alternative Route Finder-FLOOgin Report.pdf  " + '\n' + clR + " View Report ? " + clRs 
	#msgBox = QtGui.QMessageBox()
 	#msgBox.setText(str(textToShow))
 	#msgBox.setInformativeText(str(textSub))
 	#msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
	#msgBox.setWindowTitle("Alternative Route Finder - Report Generation")
 	#ret = msgBox.exec_();
	#if (ret == msgBox.Ok):
		#webbrowser.open(r'file:///home/kasun/Alternative Route Finder-FLOOgin Report.pdf')
	##Merge PDF files
	filenames = []
	filenames.append('Alternative Route Finder-FLOOgin Report.pdf')
	filenames.append('Roads_inundated_Summary.pdf')
	merger = PdfFileMerger()
	for filename in filenames:
    		merger.append(PdfFileReader(file(filename, 'rb')))
	merger.write('Alternative Route Finder-FLOOgin Report.pdf')
	#view report dialog
	# show the dialog
        self.dlgViewR.show()
	self.dlgViewR.uiViewR.txtReportNameRoad.setText('Alternative Route Finder-FLOOgin Report')
	#self.dlgViewR.uiViewR.txtReportNameRoad.end(True)
	self.dlgViewR.uiViewR.lblViewRepRoad.setVisible(False)
	self.dlgViewR.uiViewR.btnOKReport.setVisible(False)
	self.dlgViewR.uiViewR.btnNotNowReport.setVisible(False)
	self.dlgViewR.uiViewR.btnEmailRep.setVisible(False)
        # Run the dialog event loop
        self.dlgViewR.exec_()


    def showReportRoad(self):
	#webbrowser.open('Alternative Route Finder-FLOOgin Report.pdf')
	global repName
	webbrowser.open(str(repName))
	#self.dlgViewR.hide()


    def renameViewReportRoad(self):
	global repName
	rep = self.dlgViewR.uiViewR.txtReportNameRoad.text()
	repName = str(rep) + '.pdf'
	os.rename('Alternative Route Finder-FLOOgin Report.pdf',str(repName))
	self.dlgViewR.uiViewR.lblViewRepRoad.setVisible(True)
	self.dlgViewR.uiViewR.btnOKReport.setVisible(True)
	self.dlgViewR.uiViewR.btnNotNowReport.setVisible(True)
	self.dlgViewR.uiViewR.btnEmailRep.setVisible(True)

    def emailReportRoad(self):
	global repName
	self.dlgViewR.hide()
	self.dlgEmailR.uiEmailR.lblReportAttached.setText(str(repName))
	self.dlgEmailR.uiEmailR.lblRepAttachedOk.setVisible(True)
	self.dlgEmailR.uiEmailR.txtPasswordRep.setEchoMode(QtGui.QLineEdit.Password)
	self.dlgEmailR.show()
	self.dlgEmailR.exec_()


    def gmailEmailReportRoad(self):
	global host
	global port
	host = 'smtp.gmail.com'
	port = 587
	self.dlgEmailR.uiEmailR.txtUsernameRep.setText("@gmail.com")
	self.dlgEmailR.uiEmailR.txtFromRep.setText("@gmail.com")

    def hotmailEmailReportRoad(self):
	global host
	global port
	host = 'smtp.live.com'
	port = 587
	self.dlgEmailR.uiEmailR.txtUsernameRep.setText("@hotmail.com")
	self.dlgEmailR.uiEmailR.txtFromRep.setText("@hotmail.com")

    def yahooEmailReportRoad(self):
	global host
	global port
	host = 'smtp.mail.yahoo.com'
	port = 465
	self.dlgEmailR.uiEmailR.txtUsernameRep.setText("@yahoo.com")
	self.dlgEmailR.uiEmailR.txtFromRep.setText("@yahoo.com")

    def handleEditingFinishedUN(self):
	print "done"
	usernmR = self.dlgEmailR.uiEmailR.txtUsernameRep.text()
	self.dlgEmailR.uiEmailR.txtFromRep.setText(str(usernmR))

	
    def sendEmailReportRoad(self):
	## email send
	#attach file
	##msg = MIMEMultipart()
	##msg.attach(MIMEText(file("Alternative_routes.pdf").read()))
	#fp=open("Alternative_routes.pdf","rb")
	#msg=MIMEMultipart("this is a test")
	#body=MIMEText(fp.read())
	#fp.close()
	#msg.attach(body)
	# PDF attachment
	global repName
	global host
	global port
	usernameR = self.dlgEmailR.uiEmailR.txtUsernameRep.text()
	passwordR = self.dlgEmailR.uiEmailR.txtPasswordRep.text()
	fromR = self.dlgEmailR.uiEmailR.txtFromRep.text()
	toR = self.dlgEmailR.uiEmailR.txtToRep.text()
	subjectR = self.dlgEmailR.uiEmailR.txtSubjectRep.text()
	if host == '' and port == 0:
		host = 'smtp.gmail.com'
		port = 587
	else:
		hostt = str(host)
		portt = port

	msg = email.mime.Multipart.MIMEMultipart()
	msg['Subject'] = str(subjectR)
	filename = str(repName)
	fp = open(filename,'rb')
	att = email.mime.application.MIMEApplication(fp.read(),_subtype="pdf")
	fp.close()
	att.add_header('Content-Disposition','attachment',filename=filename)
	msg.attach(att)	
	#send
	fromAdd = str(fromR)
	toAdd = str(toR)
	username = str(usernameR)
	password = str(passwordR)
	#mailer = smtplib.SMTP(host='smtp.gmail.com', port=587)
	#mailer.connect()
	#mailer.login(username , password)
	#mailer.sendmail(fromAdd, toAdd, msg.as_string())
	#mailer.close()

	try:
		server = smtplib.SMTP(host=hostt, port=portt)
		#server = smtplib.SMTP(host='smtp.live.com', port=587)
		#SMTP HOST: smtp.mail.yahoo.com
		#SMTPPORT: 465   
		server.starttls()  
		server.login(username,password)  
		server.sendmail(fromAdd, toAdd, msg.as_string())  
		server.quit()
		self.dlgEmailR.hide()
		self.clearEmailReportRoad() 
		# messagebox
		colBl = '<font color="blue">'
		colBls = '</font>'	
		textToShow = "Report sent successfully" + '\n'
		textSub = colBl + "To : " + colBls + str(toR)
		msgBox = QtGui.QMessageBox()
 		msgBox.setText(str(textToShow))
 		msgBox.setInformativeText(str(textSub))
 		msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
		msgBox.setWindowTitle("Alternative Route Finder - Report Sent")
 		ret = msgBox.exec_();	
	except:
		#self.dlgEmailR.hide()
		e = sys.exc_info()[0]
		print e
		#messagebox
		if str(e) == "<class 'smtplib.SMTPAuthenticationError'>":
			textToShow = "Sorry. Your username or password is incorrect."
			winTitle = "Error : Invalid Login Details"
			print "erroor"
		else:
			textToShow = "Sorry. There is a problem in your internet connection"
			winTitle = "Error : Connection Timeout"
			print "err"
		
		colBl = '<font color="blue">'
		colBls = '</font>'	
		#textToShow = "Sorry. There is a problem in your internet connection"
		textSub = colBl + " Try agian ? " + colBls
		msgBox = QtGui.QMessageBox()
 		msgBox.setText(str(textToShow))
 		msgBox.setInformativeText(str(textSub))
 		msgBox.setStandardButtons( QMessageBox.Ok | QMessageBox.Cancel )
		msgBox.setDefaultButton( QMessageBox.Ok )
		msgBox.setWindowTitle(str(winTitle))
 		ret = msgBox.exec_();

		if (ret == msgBox.Ok):
			self.sendEmailReportRoad()	
		else:
			if str(winTitle) == "Error : Connection Timeout":
				self.clearEmailReportRoad()
				#self.dlgEmailR.hide()	

		
    def clearEmailReportRoad(self):
	self.dlgEmailR.uiEmailR.txtUsernameRep.clear()
	self.dlgEmailR.uiEmailR.txtPasswordRep.clear()
	self.dlgEmailR.uiEmailR.txtFromRep.clear()
	self.dlgEmailR.uiEmailR.txtToRep.clear()
	self.dlgEmailR.uiEmailR.txtSubjectRep.clear()
	self.dlgEmailR.uiEmailR.txtUsernameRep.setText("<Type your Username here>")
	self.dlgEmailR.uiEmailR.txtPasswordRep.setText("<Type your password here>")
	self.dlgEmailR.uiEmailR.txtFromRep.setText("<Type your E-mail address here>")
	self.dlgEmailR.uiEmailR.txtToRep.setText("<Type the recipient E-mail address here>")
	self.dlgEmailR.uiEmailR.txtSubjectRep.setText("<Type a subject for your e-mail here>")


    def exitEmailReportRoad(self):
	self.dlgEmailR.hide()

    def closeViewReportRoad(self):
	self.dlgViewR.hide()


    def getLayerByName(self, layerName):
	allLayerss = self.canvas.layers()
	for sLayer in allLayerss:
		if str(sLayer.name()) == str(layerName):
			#ccLayer = sLayer
			return sLayer 
	#return ccLayer

    def selectStart(self):
	#global okNow
	#okNow = 1
     #if (state==Qt.Checked):
	#if okNow == 1:
		#self.addLabel()
		#global stopNow
		#stopNow = 1
		self.labelPos.clear()
		global stopPlace
		stopPlace = 1
		#self.pointCursor()
		self.place()
             # connect to click signal
	#print "come new"
	#elif okNow == 2:
		#global resultCon 
     		QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownStart)
		#print val
             # connect our select function to the canvasClicked signal
        	QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeatureStart)
		#print val 
		#if resultCon == False:
			#print "falsecome"
			#global val
			#val = 1
		#self.pointCursor()
	#print str(result)
     #else:
             # disconnect from click signal
             #QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDown)
             # disconnect our select function to the canvasClicked signal
             #QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeature)    
    
    def selectStop(self):
	self.labelPos.clear()
	global stopPlace
	stopPlace = 1	
	self.place()
     #if (state==Qt.Checked):
             # connect to click signal
      	QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownStop)
             # connect our select function to the canvasClicked signal
        QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeatureStop)
     #else:
             # disconnect from click signal
             #QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDown)
             # disconnect our select function to the canvasClicked signal
             #QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeature)  



    def handleMouseDownStart(self, point, button):
        #global val
        #val = 3
	#print "handle"
	self.labelPos.clear()
        cLayer = self.canvas.currentLayer()
	cLayer.removeSelection()
	self.dlg.clearTextBrowserStart()
        self.dlg.setTextBrowserStart( "<b>X :</b> "+str(point.x()) + " , <b>Y</b> : " +str(point.y()) )
	global x1
	global y1		
	x1=float(str(point.x()))
	y1=float(str(point.y()))		
	#global val
	#val = 0
        #QMessageBox.information( self.iface.mainWindow(),"Info", "X,Y = %s,%s" % (str(point.x()),str(point.y())) )
	# disconnect from click signal
        QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownStart)
        # disconnect our select function to the canvasClicked signal
        #QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeatureStart) 

    def handleMouseDownStop(self, point, button):
	#global val
	#val = 3
	self.labelPos.clear()
        cLayer = self.canvas.currentLayer()
	#cLayer.removeSelection()
        self.dlg.clearTextBrowserStop()
        self.dlg.setTextBrowserStop( "<b>X</b> : "+str(point.x()) + " , <b>Y</b> : " +str(point.y()) )
	self.dlg.ui.lblWarnRoad.setVisible(True)
	global x2
	global y2		
	x2=float(str(point.x()))
	y2=float(str(point.y()))		

        #QMessageBox.information( self.iface.mainWindow(),"Info", "X,Y = %s,%s" % (str(point.x()),str(point.y())) )
	# disconnect from click signal
        QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDownStop)
        # disconnect our select function to the canvasClicked signal
        #QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeatureStop) 

    def selectFeatureStart(self, point, button):
       #global val
       #val = 3
       #print "selct"
       #QMessageBox.information( self.iface.mainWindow(),"Info", "in selectFeature function" )
       # setup the provider select to filter results based on a rectangle
       pntGeom = QgsGeometry.fromPoint(point)
       # scale-dependent buffer of 2 pixels-worth of map units
       pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       rect = pntBuff.boundingBox()
       # get currentLayer and dataProvider
       cLayer = self.canvas.currentLayer()
       selectList = []
       if cLayer:
	       self.markStart()
               provider = cLayer.dataProvider()
               feat = QgsFeature()
               # create the select statement
               #provider.select([],rect) # the arguments mean no attributes returned, and do a bbox filter with our buffered rectangle to limit the amount of features
               #print "comee1"
	       request = QgsFeatureRequest().setFilterRect(rect)
	       #while provider.nextFeature(feat):
               #while cLayer.getFeatures(request).next():
	       #print "comee2"
	       for feature in cLayer.getFeatures(request):
		       #print "comee"
                       # if the feat geom returned from the selection intersects our point then put it in a list
                       #if feat.geometry().intersects(pntGeom):
 	       #feature = cLayer.getFeatures(request).next()
	               feature = cLayer.getFeatures(request).next()
               #ERROR***********************************************************************
	       #selectList.append(feature.id())
	               global fid
                       fid=feature.id()
	       #selectList[0]=feature.id()
	       #QMessageBox.information( self.iface.mainWindow(),"Info", str(feature.id()) )
               #if self.selectList:
                       # make the actual selection
               #self.cLayer.setSelectedFeatures(self.selectList)
	       #self.cLayer.select(self.selectList)
	               #self.cLayer.select(fid)
		
		       #mark vertex (selection)
		       #global x1
		       #global y1
		       #global m1
		       #m1 = QgsVertexMarker(self.canvas)
		       #m1.setCenter(QgsPoint(x1,y1))
		       #m1.setColor(QColor(0,255,0))
		       #m1.setIconSize(6)
                       #m1.setIconType(QgsVertexMarker.ICON_BOX) # ICON_CROSS, ICON_X
                       #m1.setPenWidth(5)
                       # update the TextBrowser
	       #QMessageBox.information( self.iface.mainWindow(),"Info", "in selectFeature function" )
                       self.updateTextBrowserStart()

       else:
               QMessageBox.information( self.iface.mainWindow(),"Info", "No layer currently selected in TOC" )    

    def markStart(self):
	global x1
	global y1
	global m1
	m1 = QgsVertexMarker(self.canvas)
	m1.setCenter(QgsPoint(x1,y1))
	m1.setColor(QColor(0,0,255))
	m1.setIconSize(6)
        m1.setIconType(QgsVertexMarker.ICON_BOX) # ICON_CROSS, ICON_X
        m1.setPenWidth(5)




    def selectFeatureStop(self, point, button):
       #QMessageBox.information( self.iface.mainWindow(),"Info", "in selectFeature function" )
       # setup the provider select to filter results based on a rectangle
       pntGeom = QgsGeometry.fromPoint(point)
       # scale-dependent buffer of 2 pixels-worth of map units
       pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       rect = pntBuff.boundingBox()
       # get currentLayer and dataProvider
       cLayer = self.canvas.currentLayer()
       selectList = []
       if cLayer:
	       self.markStop()
               provider = cLayer.dataProvider()
               feat = QgsFeature()
               # create the select statement
               #provider.select([],rect) # the arguments mean no attributes returned, and do a bbox filter with our buffered rectangle to limit the amount of features
               request = QgsFeatureRequest().setFilterRect(rect)
	       #while provider.nextFeature(feat):
               #while cLayer.getFeatures(request).next():
	       for feature in cLayer.getFeatures(request):
                       # if the feat geom returned from the selection intersects our point then put it in a list
                       #if feat.geometry().intersects(pntGeom):
 	       	       feature = cLayer.getFeatures(request).next()
               #ERROR***********************************************************************
	       #selectList.append(feature.id())
	       	       global fid
                       fid=feature.id()
	       #selectList[0]=feature.id()
	       #QMessageBox.information( self.iface.mainWindow(),"Info", str(feature.id()) )
               #if self.selectList:
                       # make the actual selection
               #self.cLayer.setSelectedFeatures(self.selectList)
	       #self.cLayer.select(self.selectList)
	               #self.cLayer.select(fid)
                       
		       #mark vertex (selection)
		       #global x2
		       #global y2
		       #global m2
		       #m2 = QgsVertexMarker(self.canvas)
		       #m2.setCenter(QgsPoint(x2,y2))
		       #m2.setColor(QColor(0,255,0))
		       #m2.setIconSize(6)
                       #m2.setIconType(QgsVertexMarker.ICON_BOX) # ICON_CROSS, ICON_X
                       #m2.setPenWidth(5)

		       # update the TextBrowser
	       #QMessageBox.information( self.iface.mainWindow(),"Info", "in selectFeature function" )
                       self.updateTextBrowserStop()

       else:
               QMessageBox.information( self.iface.mainWindow(),"Info", "No layer currently selected in TOC" )    

    def markStop(self):
	global x2
	global y2
	global m2
	m2 = QgsVertexMarker(self.canvas)
	m2.setCenter(QgsPoint(x2,y2))
	m2.setColor(QColor(0,0,255))
	m2.setIconSize(6)
        m2.setIconType(QgsVertexMarker.ICON_BOX) # ICON_CROSS, ICON_X
        m2.setPenWidth(5)


    #def selectFeatureStop(self, point, button):
       #QMessageBox.information( self.iface.mainWindow(),"Info", "in selectFeature function" )
       # setup the provider select to filter results based on a rectangle
       #pntGeom = QgsGeometry.fromPoint(point)
       # scale-dependent buffer of 2 pixels-worth of map units
       #pntBuff = pntGeom.buffer( (self.canvas.mapUnitsPerPixel() * 2),0)
       #rect = pntBuff.boundingBox()
       # get currentLayer and dataProvider
       #cLayer = self.canvas.currentLayer()
       #selectList = []
       #if cLayer:
       #        provider = cLayer.dataProvider()
       #        feat = QgsFeature()
       #        # create the select statement
       #        provider.select([],rect) # the arguments mean no attributes returned, and do a bbox filter with our buffered rectangle to limit the amount of features
       #        while provider.nextFeature(feat):
       #                # if the feat geom returned from the selection intersects our point then put it in a list
       #                if feat.geometry().intersects(pntGeom):
       #                        selectList.append(feat.id())

               # make the actual selection
       #        cLayer.setSelectedFeatures(selectList)
       #else:
       #        QMessageBox.information( self.iface.mainWindow(),"Info", "No layer currently selected in TOC" )    

    def updateTextBrowserStart(self):
    	# if we have a selected feature
    	#if self.selectList:
	global fid
        if(fid!=0):
		cLayer = self.canvas.currentLayer()
            	self.provider = cLayer.dataProvider()
		#QMessageBox.information( self.iface.mainWindow(),"Info", "in updatetext function" )
        	# find the index of the 'NAME' column, branch if has one or not
        	##nIndx = self.provider.fieldNameIndex('NAME')
        	# get our selected feature from the provider, but we have to pass in an empty feature and the column index we want
        	#sFeat = QgsFeature()
        #if self.provider.featureAtId(self.selectList[0], sFeat, True, [nIndx]):
            # only if we have a 'NAME' column
		request = QgsFeatureRequest().setFilterFid(fid)
		feature = cLayer.getFeatures(request).next()
                self.dlg.clearTextBrowserDesStart()
		fields = cLayer.pendingFields()
		boldOpp = '<b>'
		boldCll = '</b>'
		##firstCol = boldOpp + str(fields.field(0).name()) + boldCll + " : " + str(feature[0])
            	##if nIndx != -1:
                # get the feature attributeMap
                #attMap = sFeat.attributeMap()
                # clear old TextBrowser values
		#request = QgsFeatureRequest().setFilterFid(self.selectList[0])
		#cLayer = self.canvas.currentLayer()		
		#self.cLayer = iface.currentLayer()
		global startLabel
		fieldNm = self.getFieldName(cLayer)
	   	featrGot = feature[fieldNm]
		startLabel = featrGot
		featr = str(fieldNm) + " : " + str(featrGot)   

		global startName
		startName = "<b>Location</b> : " + str(featrGot)
		global startNameForReport
		startNameForReport = "<b>Location</b> : " + str(featrGot)
                # now update the TextBrowser with attributeMap[nameColumnIndex]
                # when we first retrieve the value of 'NAME' it comes as a QString so we have to cast it to a Python string
                #self.dlg.setTextBrowserDesStart( str( attMap[nIndx].toString() ))
		#else:
			#global startName
			#startName = str(firstCol)			
		self.dlg.setTextBrowserDesStart(str(startName))
		# disconnect our select function to the canvasClicked signal
        	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeatureStart)

    def updateTextBrowserStop(self):
    	# if we have a selected feature
    	#if self.selectList:
	global fid
        if(fid!=0):
		cLayer = self.canvas.currentLayer()
            	self.provider = cLayer.dataProvider()
		#QMessageBox.information( self.iface.mainWindow(),"Info", "in updatetext function" )
        	# find the index of the 'NAME' column, branch if has one or not
        	##nIndx = self.provider.fieldNameIndex('NAME')
        	# get our selected feature from the provider, but we have to pass in an empty feature and the column index we want
        	#sFeat = QgsFeature()
        #if self.provider.featureAtId(self.selectList[0], sFeat, True, [nIndx]):
            # only if we have a 'NAME' column
		request = QgsFeatureRequest().setFilterFid(fid)
		feature = cLayer.getFeatures(request).next()
                self.dlg.clearTextBrowserDesStop()
		fields = cLayer.pendingFields()
		boldOp = '<b>'
		boldCl = '</b>'
		##firstCol = boldOp + str(fields.field(0).name()) + boldCl + " : " + str(feature[0])
            	##if nIndx != -1:
                # get the feature attributeMap
                #attMap = sFeat.attributeMap()
                # clear old TextBrowser values
		#request = QgsFeatureRequest().setFilterFid(self.selectList[0])
		#cLayer = self.canvas.currentLayer()		
		#self.cLayer = iface.currentLayer()
		global stopLabel
		fieldNm = self.getFieldName(cLayer)
	   	featrGot = feature[fieldNm]
		stopLabel = str(featrGot)
		featr = str(fieldNm) + " : " + str(featrGot)   

		global stopName
		stopName = "<b>Location</b> : " + str(featrGot)
		global stopNameForReport
		stopNameForReport = "<b>Location</b> : " + str(featrGot)
		
		##else:
			##global stopName
			##stopName = str(firstCol)			
                # now update the TextBrowser with attributeMap[nameColumnIndex]
                # when we first retrieve the value of 'NAME' it comes as a QString so we have to cast it to a Python string
                #self.dlg.setTextBrowserDesStart( str( attMap[nIndx].toString() ))
		self.dlg.setTextBrowserDesStop(str(stopName))
        	# disconnect our select function to the canvasClicked signal
        	QObject.disconnect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.selectFeatureStop)

    def handleLayerChange(self, layer):
        self.cLayer = self.canvas.currentLayer()
        if self.cLayer:
            self.provider = self.cLayer.dataProvider()

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&FLOOgin", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
    	# set the current layer immediately if it exists, otherwise it will be set on user selection
    	self.cLayer = self.iface.mapCanvas().currentLayer()
    	#if self.cLayer: self.provider = cLayer.dataProvider()
    	# make our clickTool the tool that we'll use for now
    	self.canvas.setMapTool(self.clickTool)
	#self.canvas.mMapTool=(self.curMove)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            pass

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


