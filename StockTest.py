import yfinance as yf
import numpy as np
from PyQt5 import QtCore,QtWidgets,QtGui
from  matplotlib import pyplot as plt
import sys,csv
import CrossHairCursor as CHC
import operator
from matplotlib import pyplot

OPDict = {">":operator.gt,"=":operator.eq,">":operator.lt}

TicketList = ["0050.TW","2330.TW","^TWII","EURUSD=X","USDTWD=X","EURTWD=X"]

UnitList = ["d","y","mo","m","h","wk"]

def getTicket(Ticket:str,Period:str):
    #Interval: "1h","3d","1mo"
    #Period: ["2023-01-14","2024-01-14"]
    Ticker =yf.Ticker(Ticket)
    Data = Ticker.history(period = Period)
    return Data

def getDataMx(Data,days:int):
    High = Data["High"]
    Low = Data["Low"]
    Close = Data["Close"]

    MxList = list()
    CloseList = list()
    MiddleList = list()

    for idx,c in enumerate(Close):
        CloseList.append(c)
        MiddleList.append((High[idx]+Low[idx])/2)
    CloseData = np.flip(np.asarray(CloseList))
    MiddleData = np.flip(np.asarray(MiddleList))

    for idx in range(CloseData.shape[0]-days):
        ThisList = list()
        for ind in range(days):
            ThisList.append(MiddleData[idx+ind+1])
        MxList.append(ThisList)
    
    return np.asarray(MxList)

def getCovMx(Mx):
    pass
    
class MainWin(QtWidgets.QWidget):
    sig_FoundPoints = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("富寬肉燥飯")
        self.ColorList = ["red","blue","green","white","purple","cyan","orange"]
        self.MetricList = ["日線","日均線","RSI"]

        #self.DataSource = DataSourceGroup(self)
        #self.Metric = MetricGroup(self)
        #self.Condition = ConditionGroup(self)
        self.Metric.setDisabled(True)
        self.Condition.setDisabled(True)

        self.Layout = QtWidgets.QGridLayout()
        self.Layout.addWidget(self.DataSource,0,0,2,2)
        self.Layout.addWidget(self.Metric,2,0,2,2)
        self.Layout.addWidget(self.Condition,4,0,2,2)
        self.setLayout(self.Layout)

if __name__ == "__main__":
    Data = getTicket("^TWII","1y")
    Matrix = getDataMx(Data,5)
    print(Matrix)

    #Saya Fujiwara
    #Kuru Shichisei
    #Rina Nanase
    #Mimi
    #Suzu Ichinose
    #kawd00793
    #Yui Oba
    #松本メイ
    #葵千惠