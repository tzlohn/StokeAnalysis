from PyQt5 import QtCore,QtWidgets
import sys
import numpy as np
import pyqtgraph as pg
import random

"""Crosshair Plot Widget Example"""

class CrosshairPlotWidget(QtWidgets.QWidget):
    """Scrolling plot with crosshair"""

    def __init__(self, parent=None):
        super(CrosshairPlotWidget, self).__init__(parent)

        # Use for time.sleep (s)
        self.FREQUENCY = 25
        # Use for timer.timer (ms)
        self.TIMER_FREQUENCY = self.FREQUENCY * 1000

        self.LEFT_X = -10
        self.RIGHT_X = 0
        self.x_axis = np.arange(self.LEFT_X, self.RIGHT_X, self.FREQUENCY)
        self.buffer = int((abs(self.LEFT_X) + abs(self.RIGHT_X))/self.FREQUENCY)
        self.data = []

        self.crosshair_plot_widget = pg.PlotWidget()
        self.crosshair_plot_widget.setXRange(self.LEFT_X, self.RIGHT_X)
        self.crosshair_plot_widget.setLabel('left', 'Value')
        self.crosshair_plot_widget.setLabel('bottom', 'Time (s)')
        self.crosshair_color = (196,220,255)

        self.crosshair_plot = self.crosshair_plot_widget.plot()

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

        self.start()

    def plot_updater(self):
        """Updates data buffer with data value"""

        self.data_point = random.randint(1,101)
        if len(self.data) >= self.buffer:
            del self.data[:1]
        self.data.append(float(self.data_point))
        self.crosshair_plot.setData(self.x_axis[len(self.x_axis) - len(self.data):], self.data)

    def update_crosshair(self, event):
        """Paint crosshair on mouse"""

        coordinates = event[0]  
        if self.crosshair_plot_widget.sceneBoundingRect().contains(coordinates):
            mouse_point = self.crosshair_plot_widget.plotItem.vb.mapSceneToView(coordinates)
            index = mouse_point.x()
            if index > self.LEFT_X and index <= self.RIGHT_X:
                self.crosshair_plot_widget.setTitle("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y=%0.1f</span>" % (mouse_point.x(), mouse_point.y()))
            self.vertical_line.setPos(mouse_point.x())
            self.horizontal_line.setPos(mouse_point.y())

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.plot_updater)
        self.timer.start(self.get_timer_frequency())

    def get_crosshair_plot_layout(self):
        return self.layout

    def get_timer_frequency(self):
        return self.TIMER_FREQUENCY

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

    ml.addLayout(crosshair_plot.get_crosshair_plot_layout(),0,0)

    mw.show()

    ## Start Qt event loop unless running in interactive mode or using pyside.
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()