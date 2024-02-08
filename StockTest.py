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

def alignData(Data:list)->list:
    # All data are stored in a list, every data in the data list are flipped
    # which means the newest data is in index 0. The tail of the longer one will be cutted
    # So for example, the shortest one has 5 element shorter than the longest one, then
    # every data is aligned to the shortest one, and the longest data will start from day 5 (which is positioned in the end index of the data)

    DataLength = list()
    for datum in Data:
        DataLength.append(len(datum))
    minL = min(DataLength)
    minIdx = DataLength.index(minL)
    minKey = min(Data[minIdx].keys())

    OutputList = list()
    for idx,datum in enumerate(Data):
        for idx in range(min(list(datum.keys())),minKey,1):
            datum.pop(idx)
        OutputList.append(datum)

    return OutputList

def checkCondition(BuyPrice,NowDay,aCondition)->bool:
    # op: "<",">"
    # unit: "%":percentage,"$":price
    # value: a value, depends on unit

    DataPrice = aCondition["Data"][NowDay]

    match aCondition["unit"]:
        case "%":
            value = (aCondition["value"]*0.01+1)*BuyPrice
        case "$":
            value = aCondition["value"]

    match aCondition["op"]:
        case ">":        
            if DataPrice < value:
                """
                if (DataPrice-BuyPrice)*100/BuyPrice > 3:
                    print(" %d : %.2f,%.2f"%(NowDay,DataPrice,(DataPrice-BuyPrice)*100/BuyPrice))
                """
                return False
            else:
                #print(" %d : %.2f,%.2f"%(NowDay,DataPrice,(DataPrice-BuyPrice)*100/BuyPrice))
                return True
        case "<":
            if DataPrice > value:
                return False
            else:
                return True
def checkLogic(LogicResult,OpList):
    return 

def getSellData(BuyDict:dict,NowData:dict,SellConditions:list,Condition:list)->list:
    # NowData: Full data of a tag ("Close","High"), which can be different from Buy price
    # SellConditions is a list of dict, the key of dict is SellValue,op,and unit
    # Condition is a list including a series of "and", "or", the length of the list should be -1 of SellConditions
    # Data: Data used to compare coniditons, note that the index must be aligned correctly
    # op: "<",">"
    # unit: "%":percentage,"$":price
    # value: a value, depends on unit
    # if "%" in unit is used, and it want to use to indicate "price falling", then fill the value with negative number
    # return a sell price from Data
    [Days,Prices] = convert2List(NowData)

    SellDict = dict()
    for BuyDay,BuyPrice in BuyDict.items():
        print("%d : %.2f"%(BuyDay,BuyPrice))
        for NowDay,NowPrice in zip(Days,Prices):
            if NowDay <= BuyDay:
                continue
            n = 0
            CheckResult = list()
            for aCond in SellConditions:
                CheckResult.append(checkCondition(BuyPrice,NowDay,aCond))
            print(CheckResult)
            if checkLogic(CheckResult,Condition):
                SellDict[BuyDay] = (NowDay,BuyPrice,NowPrice)
                break #the sell price for this buy price has been found, so the loop for NowDay can be broken.

    return SellDict      

def convert2List(DataDict):
    return [list(DataDict.keys()),list(DataDict.values())]

def printDict(Data:dict):
    for key,value in Data.items():
        print("%d: %.2f"%(key,value))

def getBuyData(OriData,BuyCondition:list, Conditions:list) -> dict:
    # OriData: Data to get buyprice
    # BuyCondition: list of dicts
    # "Data": dict
    # "op": ">","<"
    # "value": float
    # "unit": "%","$"
    #Condition is a list including a series of "and", "or", the length of the list should be -1 of SellConditions
    Output = list()
    for aCondition in BuyCondition:
        result = list()
        for idx,price in aCondition["Data"].items():
            match aCondition["op"]:
                case "<":
                    if price < aCondition["value"]:
                        result.append(idx)
                case ">":
                    if price > aCondition["value"]:
                        result.append(idx)
        Output.append(result)

    for idx,cond in enumerate(Conditions):
        result1 = Output.pop(0)
        result2 = Output.pop(0)
        if cond == "and":
            NewResult = list()
            for a in result2:
                if a in result1:
                    NewResult.append(a)
        elif cond == "or":
            NewResult = result2.copy()
            for a in result2:
                if not a in result1:
                    NewResult.append(a)
        Output.insert(0,NewResult)
    
    Output = Output[0]
    BuyDict = dict()
    for BuyDay in Output:
        BuyDict[BuyDay] = OriData[BuyDay]

    return BuyDict

def getTicket(Ticket:str,Period:str):
    #Interval: "1h","3d","1mo"
    #Period: ["2023-01-14","2024-01-14"]
    Ticker =yf.Ticker(Ticket)
    Data = Ticker.history(period = Period)
    #outputTable(Data)
    #printLinebyLine(Data)
    return Data

def getRollingAvg(data,days = 10):
    length = len(data)
    M1 = np.tri(length-days+1,length,days-1)
    M2 = np.flip(M1,0)
    M3 = np.flip(M2,1)
    Operator = (M1+M3)-1
    #OneRow = Operator[0,:]
    #print(np.sum(OneRow))
    Data = np.asarray(list(data.values()))
    result = np.dot(Operator,Data)/days
    result = np.ndarray.tolist(result)

    MaxIdx = max(list(data.keys()))
    minIdx = min(list(data.keys()))           
    Output = dict()
    for idx in range(Days+minIdx,MaxIdx+1,1):
        #Output[idx] = result[resultLen-(idx-days+1)]
        Output[idx] = result[idx-(days+minIdx)]

    #pyplot.imshow(M1)
    #pyplot.show()
    return Output

def getFormatedData(Data:dict,tag:str,shift:int = 0) -> dict:
    # Formated Data is a dict with index as key and price as keyword
    # Data: all data including High,Low,Close,Open
    # tag can be "High","Low","Close","Open"
    TagData = Data[tag]
    OutputData = dict()
    for idx,datum in enumerate(TagData.values):
        OutputData[idx+shift] = datum

    minidx = min(list(OutputData.keys()))
    for idx in range(shift):
        OutputData.pop(idx+len(TagData))

    return OutputData

def getDiffData(Data1:dict,Data2:dict)->dict:
    if len(Data1) != len(Data2):
        print("please align the data first")
        return False
    
    d1 = np.asarray(list(Data1.values()))
    d2 = np.asarray(list(Data2.values()))
    d = d1-d2
    LenDiff = max(Data1.keys())-len(Data1)
    Output = dict() 
    for key in Data1.keys():
        Output[key] = d[key-LenDiff-1]
    
    return Output

def getDayDiffMx(Data:dict,days:int):
    Data = np.asarray(list(Data.values()))
    for idx in range(Data.shape[0]-days):
        ThisList = list()
        for ind in range(days-1):
            ThisList.append(Data[idx]-Data[idx+ind+1])
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
    return MxList

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

    Data = getTicket("^TWII","4y")
    Data0 = getFormatedData(Data,"Close",0)
    DataN1 = getFormatedData(Data,"Close",1)
    AData0 = getRollingAvg(getFormatedData(Data,"Close",0))
    ADataN1 = getRollingAvg(getFormatedData(Data,"Close",1))
    ADataN2 = getRollingAvg(getFormatedData(Data,"Close",2))
    [Data0,AData0,ADataN1,ADataN2] = alignData([Data0,AData0,ADataN1,ADataN2])
    DataD1 = getDiffData(AData0,ADataN1)
    DataD2 = getDiffData(ADataN1,ADataN2)

    BuyCondition1 = {"Data":DataD1,"op":">","value":0,"unit":"%"}
    BuyCondition2 = {"Data":DataD2,"op":">","value":0,"unit":"%"}
    SellCondition1 = {"Data":Data0,"op":">","value":4,"unit":"%"}
    SellCondition2 = {"Data":Data0,"op":"<","value":-1.5,"unit":"%"} #(Data內的數字-買入價)/買入價<1.5%
    SellCondition3 = {"Data":DataD1,"op":"<","value":0,"unit":"$"}
    SellCondition4 = {"Data":DataD2,"op":"<","value":0,"unit":"$"}

    BuyData = getBuyData(Data0,[BuyCondition1,BuyCondition2],["and"])
    #printDict(BuyData)
    SellData = getSellData(BuyData,Data0,[SellCondition1,SellCondition2,SellCondition3,SellCondition4],["or","or","and"])
    printDict(SellData)
    """
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
    """

    """
    result = np.polyfit(XData,YData,1)
    print(result) ################# m=0.67039896 y0=-0.04488662
    m = result[0]
    d = result[1]
    Vmin = np.min(XData)
    Vmax = np.max(YData)

    Xarray = np.asarray([Vmin,Vmax])
    #Yarray = (d+m*Xarray)/(1-m)
    Yarray = d+m*Xarray
    #pyplot.plot(Matrix[:,0])
    #pyplot.plot(Outcome)
    #print(Matrix[:,0])
    #pyplot.scatter(Coor1,Coor3,c = AToutcome[:-RollingDays],cmap="RdYlGn",vmin=-10,vmax=10)
    #pyplot.scatter(Matrix[:,0],Matrix[:,1],c = Outcome[:-RollingDays],cmap="RdYlGn")
    #pyplot.scatter(Matrix[:,0],AToutcome[:-RollingDays],marker="o", c = Label[:-RollingDays],vmin=0,vmax=10)
    #pyplot.scatter(Matrix[:,0],Matrix[:,0]*(0.682/(1-0.682))+(1/0.682),marker="x")
    #pyplot.scatter(Coor4,AToutcome[:-RollingDays],marker="x")
    pyplot.scatter(XData,YData,marker="x")
    pyplot.plot(Xarray,Yarray,"r--")
    pyplot.plot(Xarray,np.asarray([0,0]),"b--")
    pyplot.plot(np.asarray([0,0]),Yarray,"b--")
    pyplot.xlabel("趨勢參數 : 今天收盤(日線) - 昨天收盤(日線)")
    pyplot.ylabel("出場-進場 : 明天收盤(日線) - 今天收盤(日線)")
    pyplot.title("回測4年")
    #pyplot.title("黃色: 今日收盤 > 今日中價")
    plt_chinese()
    #pyplot.scatter(Matrix[:,2],Matrix[:,1],marker = "x")
    #pyplot.scatter(Matrix[:-1,0],Outcome[1:-RollingDays])
    #pyplot.colorbar()
    pyplot.show()
    """
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
    #Yanagi akira/miwoko/259LUXU-079
    #翼みさき