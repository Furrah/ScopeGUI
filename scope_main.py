import sys
import matplotlib
import numpy as np 


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtGui, QtWidgets

matplotlib.use('Qt5Agg')

import ScopeGuiDesign
import hardware

#oscillopscope_host = 'bi-iq-lab-scope-1'
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class Window(QtWidgets.QMainWindow, ScopeGuiDesign.Ui_MainWindow):
    def __init__(self):

        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        self.EmbedPlot()
        self.setWindowTitle("ScopeGUI")


        self.lineEdit.setText('bi-iq-lab-scope-1')

        self.pushButton.clicked.connect(self.GetDataButton)
        self.pushButton_2.clicked.connect(self.ScopeConnect)
        self.pushButton_ClearPlot.clicked.connect(self.clearPlot)
        self.checkBox_5.stateChanged.connect(self.CheckBoxGrid)
        self.pushButton_saveData.clicked.connect(self.saveFile)

        self.pushButton.setEnabled(False)

        self.storedData = []
        self.fileNames = []

    def EmbedPlot(self):

        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.toolbar = NavigationToolbar(self.sc, self)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.sc)
        self.layout.addWidget(self.toolbar)
        self.widget.setLayout(self.layout)

    def clearPlot(self):
        self.storedData = []
        self.fileNames = []
        self.sc.axes.clear()
        self.sc.draw_idle()

    def CheckBoxGrid(self):
        if self.checkBox_5.isChecked():
            self.sc.axes.grid(True)
            self.sc.draw_idle()
        else:
            self.sc.axes.grid(False)
            self.sc.draw_idle()

    def GetDataButton(self):

        C1_state = self.checkBox_CH1.isChecked()       
        C2_state = self.checkBox_CH2.isChecked()  
        C3_state = self.checkBox_CH3.isChecked()  
        C4_state = self.checkBox_CH4.isChecked()

        channelStates = [C1_state, C2_state, C3_state, C4_state]
        channel_code  = ['C1', 'C2', 'C3', 'C4']

        for i, channel in enumerate(channelStates):
            if channel == True:
                data = self.scope.getData(channel_code[i])
                self.sc.axes.plot(data[0],data[1], label = channel_code[i])
                self.storedData.append(data)
                self.fileNames.append(channel_code[i])
        # for i, channel in zip(channel_code, channelStates):
        #     if channel == True:
        #         data = self.scope.getData(i)
        #         self.sc.axes.plot(data[0],data[1], label = i)


        self.sc.axes.legend()
        self.sc.draw_idle()

    def ScopeConnect(self):

        hostname = self.lineEdit.text()
        # print(hostname)
        self.scope = hardware.Oscilloscope(hostname)
        self.pushButton.setEnabled(True)
        '''
        add an LED or notifier that the host has been connected to 
        '''

    def saveFile(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory()


        filename = self.lineEdit_fileName.text()

        if len(directory)>0:
            for name, dat in zip(self.fileNames, self.storedData):
                np.save(directory+'/'+ filename + name, dat )





def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    #app.setStyleSheet(qdarkstyle.load_stylesheet(pyside = False))
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # app.setStyleSheet(qdarkgraystyle.load_stylesheet_pyqt5())
    form = Window()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()  
