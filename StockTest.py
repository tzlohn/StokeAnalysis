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
    MiddleDiff = list()
    MiddleTom = list()

    for idx,c in enumerate(Close):
        try:
            tomorrow = (High[idx+1]+Low[idx+1])/2
            MiddleTom.append(tomorrow)
            CloseList.append(Close[idx+1]-c)
            today = (High[idx]+Low[idx])/2
            MiddleList.append(today)          
            MiddleDiff.append(tomorrow-today)
        except:
            pass
    CloseData = np.flip(np.asarray(CloseList))
    MiddleData = np.flip(np.asarray(MiddleList))
    MiddleTom = np.flip(np.asarray(MiddleTom))
    MiddleDiff = np.flip(np.asarray(MiddleDiff))
    """
    print(MiddleData)
    print(MiddleTom)
    print(MiddleDiff)
    """
    for idx in range(CloseData.shape[0]-days):
        ThisList = list()
        for ind in range(days-1):
            ThisList.append(MiddleData[idx]-MiddleData[idx+ind+1])
        MxList.append(ThisList)

    #print(np.round(MiddleDiff,decimals=2))
    """
    for idx,v in enumerate(MiddleDiff):
        try:
            print(np.round(MxList[idx],decimals=2))
        except:
            pass
    """
    return [np.asarray(MxList),MiddleDiff]

def getCovMx(Mx):
    one = np.ones(shape = (Mx.shape[0],Mx.shape[0]))
    delta = Mx-np.dot(one,Mx)/Mx.shape[0]
    CovMx =  np.dot(np.transpose(delta),delta)/Mx.shape[0]

    return CovMx

def getEigen(CovMx):
    result = np.linalg.eig(CovMx)
    #print(result)
    #eigv = np.linalg.eigvals(CovMx)
    #eigvec = np.linalg.eigh(CovMx)
    #print(np.linalg.norm(result[1][0]))
    #print(eigv)
    return result[1]

def getPCACoor(Data,Vec):
    shape = Data.shape
    NewCoor = list()
    for count in range(shape[0]):
        NewCoor.append(getNewCoor(Data[count],Vec))
    
    return np.asarray(NewCoor)

def getNewCoor(Raw,Vec):
    return np.dot(Raw,Vec)
    
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
    RollingDays = 6

    Data = getTicket("^TWII","5y")
    [Matrix,Outcome] = getDataMx(Data,RollingDays)
    CovMx = getCovMx(Matrix)
    EigVec = getEigen(CovMx)

    Coor1 = getPCACoor(Matrix,EigVec[0])
    Coor2 = getPCACoor(Matrix,EigVec[1])
    Coor3 = getPCACoor(Matrix,EigVec[2])
    Coor4 = getPCACoor(Matrix,EigVec[3])
    
    #pyplot.plot(Matrix[:,0])
    #pyplot.plot(Outcome)
    #print(Matrix[:,0])
    #pyplot.scatter(Coor1,Coor2,c = Outcome[:-RollingDays],cmap="RdYlGn")
    #pyplot.scatter(Matrix[:,0],Matrix[:,1],c = Outcome[:-RollingDays],cmap="RdYlGn")
    pyplot.scatter(Matrix[:,1],Matrix[:,2],marker="x")
    #pyplot.scatter(Matrix[:,4],Outcome[:-RollingDays])
    #pyplot.scatter(Matrix[:-1,0],Outcome[1:-RollingDays])
    #pyplot.colorbar()
    pyplot.show()

    #Saya Fujiwara
    #Kuru Shichisei
    #Rina Nanase
    #Mimi
    #Suzu Ichinose
    #kawd00793
    #Yui Oba
    #松本メイ
    #葵千惠
    #Misuzu Tachibana