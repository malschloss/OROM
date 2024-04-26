import sys
import os
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
from random import randrange, uniform
from PyQt5 import QtTest
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from DataReader import DataReader
import pyqtgraph as pg

class SpillCharts(QWidget):
    def __init__(self):
        super().__init__()
        layout=QVBoxLayout()
        self.vtxPlot=pg.plot()
        self.vtyPlot=pg.plot()
        self.vtzPlot=pg.plot()
        self.vtxPlot.showGrid(x=True,y=True)
        self.vtxPlot.setLabel('bottom',"Spill ID")
        self.vtxPlot.setLabel('left',"X Vertex (cm)")
        self.vtyPlot.showGrid(x=True,y=True)
        self.vtyPlot.setLabel('bottom',"Spill ID")
        self.vtyPlot.setLabel('left',"Y Vertex (cm)")
        self.vtzPlot.showGrid(x=True,y=True)
        self.vtzPlot.setLabel('bottom',"Spill ID")
        self.vtzPlot.setLabel('left',"Z Vertex (cm)")
        layout.addWidget(self.vtxPlot)
        layout.addWidget(self.vtyPlot)
        layout.addWidget(self.vtzPlot)
        self.setLayout(layout)
        
        self.runButton=QPushButton("Run")
        self.runButton.setCheckable(True)
        self.runButton.setChecked(False)
        self.runButton.clicked.connect(self.UpdateChart)
        layout.addWidget(self.runButton)
        
        self.reader = None

        self.MAX_SPILLS = 5
        self.xScatter = []
        self.yScatter = []
        self.zScatter = []
        self.xErr = []
        self.yErr = []
        self.zErr = []
        self.currentFile = 0
        self.position = 0

        if not (os.path.exists("SpillVertexMeans")):
            path = os.path.join("SpillVertexMeans")
            os.mkdir(path)


        self.filenames = sorted([filename for filename in os.listdir("Reconstructed") if filename.endswith(".npy")])
        self.fileCount = len(self.filenames)
        while (self.fileCount > self.currentFile):
            if (self.currentFile >= self.MAX_SPILLS):
                self.vtxPlot.removeItem(self.xScatter[self.position])
                self.vtyPlot.removeItem(self.yScatter[self.position])
                self.vtzPlot.removeItem(self.zScatter[self.position])
                self.vtxPlot.removeItem(self.xErr[self.position])
                self.vtyPlot.removeItem(self.yErr[self.position])
                self.vtzPlot.removeItem(self.zErr[self.position])
            self.reader = DataReader([os.path.join("Reconstructed", filename) for filename in self.filenames], "EVENT")
            self.reader.current_index = self.currentFile
            self.reader.grab = "EVENT"
            self.eidData = np.array(self.reader.read_data())
            self.reader.grab = "XVERTEX"
            self.vtxData = np.array(self.reader.read_data())
            self.reader.grab = "YVERTEX"
            self.vtyData = np.array(self.reader.read_data())
            self.reader.grab = "ZVERTEX"
            self.vtzData = np.array(self.reader.read_data())
            self.reader.grab = "SPILL"
            self.sidData = np.array(self.reader.read_data()[0])
            self.vtxMean = np.array([np.mean(self.vtxData)])
            self.vtyMean = np.array([np.mean(self.vtyData)])
            self.vtzMean = np.array([np.mean(self.vtzData)])
            self.vtxSTD = np.std(self.vtxData)
            self.vtySTD = np.std(self.vtyData)
            self.vtzSTD = np.std(self.vtzData)
            if (self.currentFile < self.MAX_SPILLS):
                self.xScatter.append(pg.ScatterPlotItem(size=10,brush=pg.mkBrush(0,0,255,255)))
                self.yScatter.append(pg.ScatterPlotItem(size=10,brush=pg.mkBrush(255,0,0,255)))
                self.zScatter.append(pg.ScatterPlotItem(size=10,brush=pg.mkBrush(0,255,0,255)))
                self.xErr.append(pg.ErrorBarItem(x=self.sidData,y=self.vtxMean,height=self.vtxSTD,pen=pg.mkPen(0,0,255,255),beam=0.5))
                self.yErr.append(pg.ErrorBarItem(x=self.sidData,y=self.vtyMean,height=self.vtySTD,pen=pg.mkPen(255,0,0,255),beam=0.5))
                self.zErr.append(pg.ErrorBarItem(x=self.sidData,y=self.vtzMean,height=self.vtzSTD,pen=pg.mkPen(0,255,0,255),beam=0.5))
            self.xErr[self.position] = pg.ErrorBarItem(x=self.sidData,y=self.vtxMean,height=self.vtxSTD,pen=pg.mkPen(0,0,255,255),beam=0.5)
            self.xScatter[self.position].setData(self.sidData,self.vtxMean)
            self.vtxPlot.addItem(self.xScatter[self.position])
            self.vtxPlot.addItem(self.xErr[self.position])
            self.yErr[self.position] = pg.ErrorBarItem(x=self.sidData,y=self.vtyMean,height=self.vtySTD,pen=pg.mkPen(255,0,0,255),beam=0.5)
            self.yScatter[self.position].setData(self.sidData,self.vtyMean)
            self.vtyPlot.addItem(self.yScatter[self.position])
            self.vtyPlot.addItem(self.yErr[self.position])
            self.zErr[self.position] = pg.ErrorBarItem(x=self.sidData,y=self.vtzMean,height=self.vtzSTD,pen=pg.mkPen(0,255,0,255),beam=0.5)
            self.zScatter[self.position].setData(self.sidData,self.vtzMean)
            self.vtzPlot.addItem(self.zScatter[self.position])
            self.vtzPlot.addItem(self.zErr[self.position])
            self.spillString = str(self.sidData)
            np.savez('SpillVertexMeans/' + self.spillString + '.npz',self.sidData,self.vtxMean,self.vtyMean,self.vtzMean,self.vtxSTD,self.vtySTD,self.vtzSTD)
            self.currentFile += 1
            self.position = self.currentFile % self.MAX_SPILLS
            layout=self.layout()

    def UpdateChart(self):
        self.dt=500
        while self.runButton.isChecked():
            self.filenames = sorted([filename for filename in os.listdir("Reconstructed") if filename.endswith(".npy")])
            self.fileCount = len(self.filenames)
            if (self.fileCount > self.currentFile):
                if (self.currentFile >= self.MAX_SPILLS):
                    self.vtxPlot.removeItem(self.xScatter[self.position])
                    self.vtyPlot.removeItem(self.yScatter[self.position])
                    self.vtzPlot.removeItem(self.zScatter[self.position])
                    self.vtxPlot.removeItem(self.xErr[self.position])
                    self.vtyPlot.removeItem(self.yErr[self.position])
                    self.vtzPlot.removeItem(self.zErr[self.position])
                self.reader = DataReader([os.path.join("Reconstructed", filename) for filename in self.filenames], "EVENT")
                self.reader.current_index = self.currentFile
                self.reader.grab = "EVENT"
                self.eidData = np.array(self.reader.read_data())
                self.reader.grab = "XVERTEX"
                self.vtxData = np.array(self.reader.read_data())
                self.reader.grab = "YVERTEX"
                self.vtyData = np.array(self.reader.read_data())
                self.reader.grab = "ZVERTEX"
                self.vtzData = np.array(self.reader.read_data())
                self.reader.grab = "SPILL"
                self.sidData = np.array(self.reader.read_data()[0])
                self.vtxMean = np.array([np.mean(self.vtxData)])
                self.vtyMean = np.array([np.mean(self.vtyData)])
                self.vtzMean = np.array([np.mean(self.vtzData)])
                self.vtxSTD = np.std(self.vtxData)
                self.vtySTD = np.std(self.vtyData)
                self.vtzSTD = np.std(self.vtzData)
                if (self.currentFile < self.MAX_SPILLS):
                    self.xScatter.append(pg.ScatterPlotItem(size=10,brush=pg.mkBrush(0,0,255,255)))
                    self.yScatter.append(pg.ScatterPlotItem(size=10,brush=pg.mkBrush(255,0,0,255)))
                    self.zScatter.append(pg.ScatterPlotItem(size=10,brush=pg.mkBrush(0,255,0,255)))
                    self.xErr.append(pg.ErrorBarItem(x=self.sidData,y=self.vtxMean,height=self.vtxSTD,pen=pg.mkPen(0,0,255,255),beam=0.5))
                    self.yErr.append(pg.ErrorBarItem(x=self.sidData,y=self.vtyMean,height=self.vtySTD,pen=pg.mkPen(255,0,0,255),beam=0.5))
                    self.zErr.append(pg.ErrorBarItem(x=self.sidData,y=self.vtzMean,height=self.vtzSTD,pen=pg.mkPen(0,255,0,255),beam=0.5))
                self.xErr[self.position] = pg.ErrorBarItem(x=self.sidData,y=self.vtxMean,height=self.vtxSTD,pen=pg.mkPen(0,0,255,255),beam=0.5)
                self.xScatter[self.position].setData(self.sidData,self.vtxMean)
                self.vtxPlot.addItem(self.xScatter[self.position])
                self.vtxPlot.addItem(self.xErr[self.position])
                self.yErr[self.position] = pg.ErrorBarItem(x=self.sidData,y=self.vtyMean,height=self.vtySTD,pen=pg.mkPen(255,0,0,255),beam=0.5)
                self.yScatter[self.position].setData(self.sidData,self.vtyMean)
                self.vtyPlot.addItem(self.yScatter[self.position])
                self.vtyPlot.addItem(self.yErr[self.position])
                self.zErr[self.position] = pg.ErrorBarItem(x=self.sidData,y=self.vtzMean,height=self.vtzSTD,pen=pg.mkPen(0,255,0,255),beam=0.5)
                self.zScatter[self.position].setData(self.sidData,self.vtzMean)
                self.vtzPlot.addItem(self.zScatter[self.position])
                self.vtzPlot.addItem(self.zErr[self.position])
                np.savez('SpillVertexMeans/' + self.spillString + '.npz',self.sidData,self.vtxMean,self.vtyMean,self.vtzMean,self.vtxSTD,self.vtySTD,self.vtzSTD)
                self.currentFile += 1
                self.position = self.currentFile % self.MAX_SPILLS
                layout=self.layout()
            QtTest.QTest.qWait(self.dt)