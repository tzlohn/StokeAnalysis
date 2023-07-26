from PyQt5 import QtCore,QtWidgets,QtGui
import sys
import numpy as np
import pyqtgraph as pg

"""Crosshair Plot Widget Example"""

class MyAxisItem(pg.AxisItem):      
    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        p.setRenderHint(p.Antialiasing, False)
        p.setRenderHint(p.TextAntialiasing, True)

        ## draw long line along axis
        pen, p1, p2 = axisSpec
        p.setPen(pen)
        p.drawLine(p1, p2)
        p.translate(0.5,0)  ## resolves some damn pixel ambiguity

        ## draw ticks
        for pen, p1, p2 in tickSpecs:
            p.setPen(pen)
            p.drawLine(p1, p2)

        ## Draw all text
        if self.style['tickFont'] is not None:
            p.setFont(self.style['tickFont'])
        p.setPen(self.textPen())
        bounding = self.boundingRect().toAlignedRect()
        Bounding = QtCore.QRect(bounding.x(),bounding.y(),bounding.width(),bounding.height()+50)
        p.setClipRect(Bounding)

        for idx, (rect, flags, text) in enumerate(textSpecs):
            p.save()
            p.rotate(-90)
            p.translate(-rect.x()-rect.width()-rect.height(),rect.x()+rect.height()*2)
            p.drawText(rect, flags, text)
            # restoring the painter is *required*!!!
            p.restore()

class CrosshairPlotWidget(QtWidgets.QWidget):
    """Scrolling plot with crosshair"""
    
    def __init__(self,data = None,x_axis=None, parent=None, title = None):
        super().__init__()

        # Use for time.sleep (s)
        self.FREQUENCY = 25
        # Use for timer.timer (ms)
        self.TIMER_FREQUENCY = self.FREQUENCY * 1000

        self.LEFT_X = 0
        self.RIGHT_X = 100

        AxisBottom = MyAxisItem(orientation="bottom")
        AxisBottom.fixedHeight = 75
        self.PlotWidget = pg.PlotWidget(axisItems={"bottom":AxisBottom})
        if title is not None:
            self.PlotWidget.setWindowTitle(title)
        self.PlotWidget.plotItem.layout.setContentsMargins(1,1,1,50)     
        self.PlotWidget.setXRange(self.LEFT_X, self.RIGHT_X)
        self.PlotWidget.setLabel('left', 'Value')
        self.PlotWidget.setLabel('bottom')
        self.crosshair_color = (196,220,255)
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.PlotWidget)

        self.PlotWidget.plotItem.setAutoVisible(y=True)
        self.vertical_line = pg.InfiniteLine(angle=90)
        self.horizontal_line = pg.InfiniteLine(angle=0, movable=False)
        self.vertical_line.setPen(self.crosshair_color)
        self.horizontal_line.setPen(self.crosshair_color)
        self.PlotWidget.setAutoVisible(y=True)
        self.PlotWidget.addItem(self.vertical_line, ignoreBounds=True)
        self.PlotWidget.addItem(self.horizontal_line, ignoreBounds=True)

        self.crosshair_update = pg.SignalProxy(self.PlotWidget.scene().sigMouseMoved, rateLimit=60, slot=self.update_crosshair)

    def update_crosshair(self, event):
        """Paint crosshair on mouse"""

        coordinates = event[0]  
        if self.PlotWidget.sceneBoundingRect().contains(coordinates):
            mouse_point = self.PlotWidget.plotItem.vb.mapSceneToView(coordinates)
            try:
                self.PlotWidget.setTitle("<span style='font-size: 12pt'>x=%s,   <span style='color: red'>y=%0.2f</span>" % (self.AxisDict[int(mouse_point.x())], mouse_point.y()))
            except:
                pass
            self.vertical_line.setPos(mouse_point.x())
            self.horizontal_line.setPos(mouse_point.y())

    def plotBoxChart(self,data,x_axis):
        #print(x_axis)
        self.PlotWidget.setXRange(0,len(data))
        self.PlotWidget.show()
        IndexData = np.arange(len(data))
        bargraph = [QtCore.QRectF() for d in data]
        #bargraph = [pg.BarGraphItem(x = IndexData[idx], height = [abs(d[1]-d[0])], width = 0.6, brush ='r' if (d[1]-d[0])>0 else 'g') for idx,d in enumerate(data)]
        self.AxisDict = dict()

        for idx,date in enumerate(x_axis):
            self.AxisDict[idx] = date

        for idx,(data,bar) in enumerate(zip(data,bargraph)):
            Low = min(data[0],data[1])
            High = max(data[0],data[1])
            bar.setBottom(Low)
            bar.setTop(High)
            bar.setRight(idx+0.3)
            bar.setLeft(idx-0.3)
            Rect = QtWidgets.QGraphicsRectItem(bar)

            if data[1] > data[0]:
                PenColor = QtCore.Qt.red   
            else:
                PenColor = QtCore.Qt.green
            
            Rect.setPen(QtGui.QPen(PenColor,0.001,QtCore.Qt.SolidLine))
            Rect.setBrush(QtGui.QBrush(PenColor, QtCore.Qt.SolidPattern))
            
            WhiskerHigh = pg.PlotCurveItem([idx,idx],[High,data[2]])
            WhiskerLow = pg.PlotCurveItem([idx,idx],[data[3],Low])
            self.PlotWidget.addItem(Rect)
            self.PlotWidget.addItem(WhiskerHigh)
            self.PlotWidget.addItem(WhiskerLow)

        Axis = self.PlotWidget.getAxis("bottom")    
        Axis.setTicks([[(value,name) for value,name in zip(list(IndexData),x_axis)]])
    
    def plot(self,data,x_axis,QColor):
        self.PlotWidget.show()
        self.PlotWidget.plotItem.plot(x_axis,data,pen = {"color" : QColor, "width" : 1,"style": QtCore.Qt.DashLine})
    
    def plotZone(self,Pos,range,color):
        if range == 0:
            Lines = list()
            for pos in Pos:
                line = pg.InfiniteLine(angle=90)
                line.setPen(QtGui.QPen(QtGui.QColor(color),0.1,QtCore.Qt.DotLine))
                self.PlotWidget.addItem(line, ignoreBounds=True)
                line.setPos(pos)
                Lines.append(line)
       
if __name__ == '__main__':
    # Create main application window
    app = QtWidgets.QApplication([])
    app.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))

    # Create and set widget layout
    # Main widget container
    cw = QtWidgets.QWidget()
    ml = QtWidgets.QGridLayout()
    cw.setLayout(ml)

    # Create crosshair plot
    crosshair_plot = CrosshairPlotWidget()
    date = ['2023-06-21', '2023-06-26', '2023-06-27', '2023-06-28', '2023-06-29', '2023-06-30', '2023-07-03', '2023-07-04', '2023-07-05', '2023-07-06', '2023-07-07', '2023-07-10', '2023-07-11', '2023-07-12', '2023-07-13', '2023-07-14', '2023-07-17', '2023-07-18', '2023-07-19', '2023-07-20', '2023-07-21']
    data = [(130.5500030517578, 130.5500030517578, 131.0500030517578, 130.25), (130.35000610351562, 129.75, 130.35000610351562, 129.39999389648438), (129.14999389648438, 128.89999389648438, 129.5500030517578, 128.6999969482422), (129.35000610351562, 129.10000610351562, 129.6999969482422, 128.8000030517578), (129.75, 129.0500030517578, 130.5, 128.89999389648438), (128.8000030517578, 129.10000610351562, 129.10000610351562, 128.3000030517578), (129.60000610351562, 130.6999969482422, 130.6999969482422, 129.60000610351562), (130.75, 131.0, 131.14999389648438, 130.5500030517578), (131.0, 130.8000030517578, 131.1999969482422, 130.39999389648438), (129.6999969482422, 127.9000015258789, 129.6999969482422, 127.69999694824219), (127.55000305175781, 127.69999694824219, 128.3000030517578, 127.0999984741211), (128.10000610351562, 127.44999694824219, 128.5, 127.0), (128.0, 129.1999969482422, 129.1999969482422, 128.0), (129.3000030517578, 129.4499969482422, 129.4499969482422, 128.85000610351562), (131.3000030517578, 130.89999389648438, 131.89999389648438, 130.85000610351562), (131.4499969482422, 132.25, 132.5, 131.4499969482422), (132.0, 132.0, 132.1999969482422, 131.75), (131.0, 129.85000610351562, 131.0, 129.6999969482422), (130.14999389648438, 128.75, 130.5, 128.75), (129.0500030517578, 129.35000610351562, 129.6999969482422, 129.0), (127.4000015258789, 127.19999694824219, 127.4000015258789, 126.5)]
    crosshair_plot.plotBoxChart(data,date)
    """
    for idx,d in enumerate(data):
        print("%d: %.2f,%.2f,%.2f,%.2f"%(idx,d[0],d[1],d[2],d[3]))
    """
    ## Start Qt event loop unless running in interactive mode or using pyside.
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()