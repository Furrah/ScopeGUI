import sys
import matplotlib

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtGui, QtWidgets

matplotlib.use('Qt5Agg')

import ScopeGuiDesign_V0
import hardware

#oscillopscope_host = 'bi-iq-lab-scope-1'
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)



class Window(QtWidgets.QMainWindow, ScopeGuiDesign_V0.Ui_MainWindow):
    def __init__(self):

        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        self.EmbedPlot()

        self.lineEdit.setText('bi-iq-lab-scope-1')

        self.pushButton.clicked.connect(self.GetDataButton)
        self.pushButton_2.clicked.connect(self.ScopeConnect)
        

    def EmbedPlot(self):

        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.sc)
        self.layout.addWidget(self.toolbar)
        self.widget.setLayout(self.layout)




    def GetDataButton(self):

        C1_state = self.checkBox.isChecked()       
        C2_state = self.checkBox_2.isChecked()  
        C3_state = self.checkBox_3.isChecked()  
        C4_state = self.checkBox_4.isChecked()

        channelStates = [C1_state, C2_state, C3_state, C4_state]

        channel_code = ['C1', 'C2', 'C3', 'C4']



        for i, channel in enumerate(channelStates):
            if channel == True:
                data = self.Oscilloscope.getData(channel_code[i])
                self.sc.axes.plot(data[0],data[1])
        # self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.sc.draw_idle()


    def ScopeConnect(self):

        hostname = self.lineEdit.text()
        print(hostname)
        self.scope = hardware.Oscilloscope(hostname)

        '''
        add an LED or notifier that the host has been connected to 
        '''




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
