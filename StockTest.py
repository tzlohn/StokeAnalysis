import yfinance as yf
import numpy as np
from PyQt5 import QtCore,QtWidgets,QtGui
from  matplotlib import pyplot as plt
import sys,csv
import CrossHairCursor as CHC
import operator
from matplotlib import pyplot
import pandas
import tkinter as tk
from tkinter import filedialog
import scipy.fftpack as FFT

root = tk.Tk()
root.withdraw()

OPDict = {">":operator.gt,"=":operator.eq,">":operator.lt}

TicketList = ["0050.TW","2330.TW","^TWII","EURUSD=X","USDTWD=X","EURTWD=X"]

UnitList = ["d","y","mo","m","h","wk"]

Days = 10

def plt_chinese():
    pyplot.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 修改中文字體
    pyplot.rcParams['axes.unicode_minus'] = False

def printLinebyLine(Data:pandas):
    for idx,a in enumerate(Data.index):
        print(a,Data["High"].values[idx],Data["Low"].values[idx],Data["Close"].values[idx],(Data["High"].values[idx]+Data["Low"].values[idx])/2)

def outputTable(Data):
    PathDir = filedialog.askdirectory()
    #PathDir = QtWidgets.QFileDialog.getExistingDirectory(caption="選擇資料夾")
    PathDir = PathDir + "/"+"報表.csv"

    TableList = list()
    
    for idx,Date in enumerate(Data.index):
        OutDict = dict()
        OutDict["日期"] = Date
        OutDict["開盤"] = round(Data["Open"].values[idx],2)
        OutDict["收盤"] = round(Data["Close"].values[idx],2)
        OutDict["最高"] = round(Data["High"].values[idx],2)
        OutDict["最低"] = round(Data["Low"].values[idx],2)
        OutDict["均價"] = round((Data["High"].values[idx]+Data["Low"].values[idx])/2,2)
        TableList.append(OutDict)

    with open(PathDir,"w+") as csvFile:
        FieldNames = ["日期","開盤","收盤","最高","最低","均價"]
        writer = csv.DictWriter(csvFile, fieldnames=FieldNames)

        writer.writeheader()
        for aDict in TableList:
            #print(aDict)
            writer.writerow(aDict)

def acorr(data):

    f_data = FFT.fft(data)
    r_data = np.flip(data)
    f_rdata = FFT.fft(r_data)
    f_corr = np.multiply(f_data,f_rdata)
    corr = FFT.fftshift(FFT.ifft(f_corr))
    corr = np.multiply(corr,np.conj(corr))

    length = corr.shape[0]
    x = np.arange(-int(length/2),int(length/2)+1,1)

    pyplot.plot(x,corr,"x-")
    pyplot.show()
      

def getTicket(Ticket:str,Period:str):
    #Interval: "1h","3d","1mo"
    #Period: ["2023-01-14","2024-01-14"]
    Ticker =yf.Ticker(Ticket)
    Data = Ticker.history(period = Period)
    #outputTable(Data)
    #printLinebyLine(Data)
    return Data

def RollingAvg(data,days = 10):

    M1 = np.tri(data.shape[0]-days+1,data.shape[0],days-1)
    M2 = np.flip(M1,0)
    M3 = np.flip(M2,1)
    Operator = (M1+M3)-1
    #OneRow = Operator[0,:]
    #print(np.sum(OneRow))
    result = np.dot(Operator,data)/days
    #pyplot.imshow(M1)
    #pyplot.show()
    return result

def getDataMx(Data,days:int):
    High = Data["High"]
    Low = Data["Low"]
    Close = Data["Close"]
    Open = Data["Open"]

    MxList = list()
    CloseList = list()
    MiddleList = list()
    MiddleDiff = list() # Difference to 1 day after
    MiddleTom = list() # Value of tomorrow
    MiddleAtom = list() # Value of the day after tomorrow
    DiffAtom = list() # Difference to 2 days after
    OpenList = list()
    ATOpenList = list()
    TCloseList = list()
    ATCloseList = list()
    ATHighList = list()
    HighList = list()

    for idx,c in enumerate(Close):
        try:
            today = (High[idx]+Low[idx])/2
            tomorrow = (High[idx+1]+Low[idx+1])/2
            AfterTom = (High[idx+2]+Low[idx+2])/2
            ATOpenList.append(Open[idx+2])
            ATCloseList.append(Close[idx+2])
            ATHighList.append(High[idx+2]) 
            TCloseList.append(Close[idx+1])
            MiddleTom.append(tomorrow)
            MiddleAtom.append(AfterTom)
            HighList.append(High[idx])
            CloseList.append(c)
            OpenList.append(Open[idx])
                       
            MiddleList.append(today)

            MiddleDiff.append(tomorrow-today)
            DiffAtom.append(AfterTom-today)
        except:
            pass
    CloseData = np.flip(np.asarray(CloseList))
    HighData = np.flip(np.asarray(HighList))
    OpenData = np.flip(np.asarray(OpenList))
    ATCloseData = np.flip(np.asarray(ATCloseList))
    TCloseData = np.flip(np.asarray(TCloseList))
    ATHighData = np.flip(np.asarray(ATHighList))
    ATOpenData = np.flip(np.asarray(ATOpenList))
    MiddleData = np.flip(np.asarray(MiddleList))
    MiddleTom = np.flip(np.asarray(MiddleTom))
    MiddleAtom = np.flip(np.asarray(MiddleAtom))
    #print(MiddleData)
    MiddleData = RollingAvg(MiddleData,Days)
    HighData = RollingAvg(HighData,Days)
    #print(MiddleData)
    AvgTom = RollingAvg(MiddleTom,Days)
    AvgAtom = RollingAvg(MiddleAtom,Days)

    #MiddleDiff = np.flip(np.asarray(MiddleDiff))
    #DiffAtom = np.flip(np.asarray(DiffAtom))
    MiddleDiff = MiddleTom[:-Days+1]-MiddleData
    #DiffAtom = MiddleAtom[:-Days+1]-MiddleData
    #DiffAtom = TCloseData[:-Days+1]-CloseData[:-Days+1]
    DiffAtom = ATCloseData[:-Days+1]-ATOpenData[:-Days+1]

    LabelData = CloseData[:-Days+1]-MiddleData # today close > today middle
    #LabelData = OpenData[:-Days+1]-CloseData[:-Days+1] # AfterTomorrow Open > Today close
    #LabelData = ATHighData[:-Days+1]-CloseData[:-Days+1]
    
    #print(MiddleData)
    #print(LabelData)
    #print(MiddleTom)
    #print(MiddleDiff)
    
    #print(MiddleData)
    #print(DiffAtom)

    acorr(CloseData)

    for idx in range(MiddleData.shape[0]-days):
        ThisList = list()
        for ind in range(days-1):
            ThisList.append(CloseData[idx]-CloseData[idx+ind+1])
            #ThisList.append(MiddleData[idx]-MiddleData[idx+ind+1])
            #ThisList.append(HighData[idx]-HighData[idx+ind+1])
        MxList.append(ThisList)
    MxList = np.asarray(MxList)
    #print(MxList[:,0])
    #print(MxList[:,1])
    #print(MxList[:,2])
    #print(np.round(MiddleDiff,decimals=2))
    """
    for idx,v in enumerate(MiddleDiff):
        try:
            print(np.round(MxList[idx],decimals=2))
        except:
            pass
    """
    return [MxList,MiddleDiff,DiffAtom,LabelData]

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

    Data = getTicket("^TWII","2y")
    [Matrix,TOutcome,AToutcome,Label] = getDataMx(Data,RollingDays)
    CovMx = getCovMx(Matrix)
    EigVec = getEigen(CovMx)
    Coor1 = getPCACoor(Matrix,EigVec[0])
    Coor2 = getPCACoor(Matrix,EigVec[1])
    Coor3 = getPCACoor(Matrix,EigVec[2])
    Coor4 = getPCACoor(Matrix,EigVec[3])
    #print(AToutcome)
    #print(Matrix[:,0].shape)
    #print(AToutcome.shape)

    #result = np.polyfit(Matrix[:,2],Matrix[:,1],1)
    result = np.polyfit(Matrix[:,0],AToutcome[:-RollingDays],1)
    print(result) ################# m=0.67039896 y0=-0.04488662
    m = result[0]
    d = result[1]
    Vmin = np.min(Matrix[:,0])
    Vmax = np.max(Matrix[:,0])
    Xarray = np.asarray([Vmin,Vmax])
    #Yarray = (d+m*Xarray)/(1-m)
    Yarray = d+m*Xarray
    #pyplot.plot(Matrix[:,0])
    #pyplot.plot(Outcome)
    #print(Matrix[:,0])
    pyplot.scatter(Coor1,Coor3,c = AToutcome[:-RollingDays],cmap="RdYlGn",vmin=-10,vmax=10)
    #pyplot.scatter(Matrix[:,0],Matrix[:,1],c = Outcome[:-RollingDays],cmap="RdYlGn")
    #pyplot.scatter(Matrix[:,0],AToutcome[:-RollingDays],marker="o", c = Label[:-RollingDays],vmin=0,vmax=10)
    #pyplot.scatter(Matrix[:,0],Matrix[:,0]*(0.682/(1-0.682))+(1/0.682),marker="x")
    #pyplot.scatter(Coor4,AToutcome[:-RollingDays],marker="x")
    pyplot.plot(Xarray,Yarray,"r--")
    pyplot.plot(Xarray,np.asarray([0,0]),"b--")
    pyplot.plot(np.asarray([0,0]),Yarray,"b--")
    pyplot.xlabel("趨勢參數 : 今天收盤(10日平均線) - 昨天收盤(10日平均線)")
    pyplot.ylabel("出場-進場 : 後天收盤(日線) - 後天開盤(日線)")
    pyplot.title("黃色: 今日收盤 > 今日中價")
    plt_chinese()
    #pyplot.scatter(Matrix[:,2],Matrix[:,1],marker = "x")
    #pyplot.scatter(Matrix[:-1,0],Outcome[1:-RollingDays])
    pyplot.colorbar()
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