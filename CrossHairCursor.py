from PyQt5 import QtCore,QtWidgets
import sys
import numpy as np
import pyqtgraph as pg
import random

"""Crosshair Plot Widget Example"""

class CrosshairPlotWidget(QtWidgets.QWidget):
    """Scrolling plot with crosshair"""

    def __init__(self,data = None,x_axis=None, parent=None):
        super().__init__()

        # Use for time.sleep (s)
        self.FREQUENCY = 25
        # Use for timer.timer (ms)
        self.TIMER_FREQUENCY = self.FREQUENCY * 1000

        self.LEFT_X = 0
        self.RIGHT_X = 100

        self.crosshair_plot_widget = pg.PlotWidget()
        self.crosshair_plot_widget.setXRange(self.LEFT_X, self.RIGHT_X)
        self.crosshair_plot_widget.setLabel('left', 'Value')
        self.crosshair_plot_widget.setLabel('bottom', 'Time (s)')
        self.crosshair_color = (196,220,255)

        #self.crosshair_plot = self.crosshair_plot_widget.plot()

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.crosshair_plot_widget)

        self.crosshair_plot_widget.plotItem.setAutoVisible(y=True)
        self.vertical_line = pg.InfiniteLine(angle=90)
        self.horizontal_line = pg.InfiniteLine(angle=0, movable=False)
        self.vertical_line.setPen(self.crosshair_color)
        self.horizontal_line.setPen(self.crosshair_color)
        self.crosshair_plot_widget.setAutoVisible(y=True)
        self.crosshair_plot_widget.addItem(self.vertical_line, ignoreBounds=True)
        self.crosshair_plot_widget.addItem(self.horizontal_line, ignoreBounds=True)

        self.crosshair_update = pg.SignalProxy(self.crosshair_plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.update_crosshair)

    def update_crosshair(self, event):
        """Paint crosshair on mouse"""

        coordinates = event[0]  
        if self.crosshair_plot_widget.sceneBoundingRect().contains(coordinates):
            mouse_point = self.crosshair_plot_widget.plotItem.vb.mapSceneToView(coordinates)
            self.crosshair_plot_widget.setTitle("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y=%0.1f</span>" % (mouse_point.x(), mouse_point.y()))
            self.vertical_line.setPos(mouse_point.x())
            self.horizontal_line.setPos(mouse_point.y())

    def plot(self,data,x_axis):
        self.crosshair_plot_widget.show()
        self.crosshair_plot_widget.plotItem.plot(x_axis,data)
        

if __name__ == '__main__':
    # Create main application window
    app = QtWidgets.QApplication([])
    app.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))
    mw = QtWidgets.QMainWindow()
    mw.setWindowTitle('Crosshair Plot Example')

    # Create and set widget layout
    # Main widget container
    cw = QtWidgets.QWidget()
    ml = QtWidgets.QGridLayout()
    cw.setLayout(ml)
    mw.setCentralWidget(cw)

    # Create crosshair plot
    crosshair_plot = CrosshairPlotWidget()

    mw.show()

    ## Start Qt event loop unless running in interactive mode or using pyside.
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()