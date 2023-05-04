import yfinance as yf
import numpy as np
from PyQt5 import QtCore,QtWidgets
from  matplotlib import pyplot as plt
import sys

class DataSourceGroup(QtWidgets.QGroupBox):
    def __init__(self,parent):
        super().__init__()

        self.MainWin = parent
        self.setTitle("資料設定")

        self.TickerLabel = QtWidgets.QLabel(parent = self,text = "代碼:")
        self.TickerBox = QtWidgets.QComboBox(self)
        self.TickerBox.addItems(["0050.TW","2330.TW"])
        self.TickerBox.currentIndexChanged.connect(self.getTicket)
        self.PeriodLabel = QtWidgets.QLabel(parent = self,text = "載入資料期間(從現在回朔):")
        self.DigitBox = QtWidgets.QSpinBox(self)
        self.DigitBox.setValue(1)
        self.DigitBox.setMinimum(1)
        self.DigitBox.setMaximum(12)
        self.DigitBox.valueChanged.connect(self.resetPeriod)
        self.UnitBox = QtWidgets.QComboBox(self)
        self.UnitBox.addItems(["日","月","年"])
        self.UnitBox.setCurrentIndex(1)
        self.UnitBox.currentIndexChanged.connect(self.changeDigitList)
        self.UnitBox.currentIndexChanged.connect(self.resetPeriod)
        self.getTicket()

        self.StartDateLabel = QtWidgets.QLabel(parent = self, text = "開始日期 (yyyy-mm-dd):")
        self.StartDate = QtWidgets.QLineEdit(self)
        self.StartDate.setText(str(self.Data.index.date[0]))
        self.EndDateLabel = QtWidgets.QLabel(parent = self, text = "結束日期 (yyyy-mm-dd):")
        self.EndDate = QtWidgets.QLineEdit(self)
        self.EndDate.setText(str(self.Data.index.date[-1]))

        self.StartButton = QtWidgets.QPushButton("開始計算")
        self.StartButton.clicked.connect(self.getData)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.TickerLabel,0,0,2,2)
        self.layout.addWidget(self.TickerBox,0,2,2,2)
        self.layout.addWidget(self.PeriodLabel,2,0,2,2)
        self.layout.addWidget(self.DigitBox,2,2,2,1)
        self.layout.addWidget(self.UnitBox,2,3,2,1)
        self.layout.addWidget(self.StartDateLabel,4,0,2,2)
        self.layout.addWidget(self.StartDate,4,2,2,2)
        self.layout.addWidget(self.EndDateLabel,6,0,2,2)
        self.layout.addWidget(self.EndDate,6,2,2,2)
        self.layout.addWidget(self.StartButton,8,1,2,2)

        self.setLayout(self.layout)
    
    def changeDigitList(self):
        if self.UnitBox.currentIndex() == 0:
            self.DigitBox.setValue(1)
            self.DigitBox.setMinimum(1)
            self.DigitBox.setMaximum(31)
        if self.UnitBox.currentIndex() == 2:
            self.DigitBox.setValue(1)
            self.DigitBox.setMinimum(1)
            self.DigitBox.setMaximum(20)
        if self.UnitBox.currentIndex() == 1:
            self.DigitBox.setValue(1)
            self.DigitBox.setMinimum(1)
            self.DigitBox.setMaximum(12)

    def transferUnit(self):
        if self.UnitBox.currentIndex() == 0:
            Unit = "d"
        if self.UnitBox.currentIndex() == 2:
            Unit = "y"
        if self.UnitBox.currentIndex() == 1:
            Unit = "mo"
        return Unit

    def getTicket(self):
        self.Ticket = yf.Ticker(self.TickerBox.currentText())
        self.Unit = self.transferUnit()
        self.Period = str(self.DigitBox.value()) + self.Unit
        self.Data = self.Ticket.history(period = self.Period)
    
    def resetPeriod(self):
        self.Unit = self.transferUnit()
        self.Period = str(self.DigitBox.value()) + self.Unit
        self.Data = self.Ticket.history(period = self.Period)
        self.resetDate()

    def resetDate(self):
        self.StartDate.setText(str(self.Data.index.date[0]))
        self.EndDate.setText(str(self.Data.index.date[-1]))

    def getData(self):
        self.PeriodData = self.Data.loc[self.StartDate.text():self.EndDate.text()]
        High = self.PeriodData["High"]
        Low = self.PeriodData["Low"]
        Close = self.PeriodData["Close"]

        Cash = 1
        BuyCount = 0
        SellCount = 0

        for n in range(1,len(High)):
            if Close[n] > High[n-1]:
                Cash = Cash - 1 # Buy
                BuyCount = BuyCount + 1
            elif Close[n] < Low[n-1]:
                Cash = Cash + 1 # Sell
                SellCount = SellCount +1
        
        Message = "這段期間裡你賺了 %d元, 其中包含了 %d次 的買進 和 %d次的 賣出"%(Cash, BuyCount, SellCount)
        QtWidgets.QMessageBox.information(None,"Result",Message)

class MetricGroup(QtWidgets.QGroupBox):
    def __init__(self,parent):
        super().__init__()

        self.MainWin = parent
        self.setTitle("技術線型")

        self.RawCB = QtWidgets.QCheckBox(self)
        self.RawCB.setText("完整資料")

        self.DayLineCB = QtWidgets.QCheckBox(self)
        self.DayLineCB.setText("日線")             

        self.Avg5CB = QtWidgets.QCheckBox(self)
        self.Avg5CB.setText("5日平均線")

        self.Avg10CB = QtWidgets.QCheckBox(self)
        self.Avg10CB.setText("10日平均線")

        self.AvgMonCB = QtWidgets.QCheckBox(self)
        self.AvgMonCB.setText("月平均線")

        self.RSI5CB = QtWidgets.QCheckBox(self)
        self.RSI5CB.setText("5日RSI")

        self.RSI10CB = QtWidgets.QCheckBox(self)
        self.RSI10CB.setText("10日RSI")

        self.PlotButton = QtWidgets.QPushButton(self)
        self.PlotButton.setText("觀察技術線")
        self.PlotButton.clicked.connect(self.plotCurves)

        self.Layout = QtWidgets.QGridLayout(self)
        self.Layout.addWidget(self.RawCB,0,0,1,2)
        self.Layout.addWidget(self.DayLineCB,0,2,1,2)
        self.Layout.addWidget(self.Avg5CB,1,0,1,2)
        self.Layout.addWidget(self.Avg10CB,1,2,1,2)
        self.Layout.addWidget(self.AvgMonCB,2,0,1,2)
        self.Layout.addWidget(self.RSI5CB,3,0,1,2)
        self.Layout.addWidget(self.RSI10CB,3,2,1,2)
        self.Layout.addWidget(self.PlotButton,4,1,1,2)

        self.setLayout(self.Layout)

    def plotCurves(self):
        pass

class MainWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.DataSource = DataSourceGroup(self)
        self.Metric = MetricGroup(self)

        self.Layout = QtWidgets.QGridLayout()
        self.Layout.addWidget(self.DataSource,0,0,2,2)
        self.Layout.addWidget(self.Metric,2,0,2,2)
        self.setLayout(self.Layout)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec_())