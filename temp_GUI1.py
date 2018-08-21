from PyQt5.QtGui import *
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import * 
import pyqtgraph as pg
import pyqtgraph.exporters
import random
import u3
import sys
import time 
import numpy as np

d = u3.U3() #initialize interface

d.configU3() #configure labjack 
d.getCalibrationData() #calibrate Labjack
d.configIO(FIOAnalog = 31) # set all channels to analog


d.streamConfig(NumChannels=1,PChannels=[30],NChannels=[31],Resolution=1,\
               ScanFrequency=10000,SamplesPerPacket=25)
'''
AIN_REGISTER = 30 # sets input to 0 default value
FIOO_STATE_REGISTER = 6000 #open the port of flexible input output.
'''


class MainWindow(QMainWindow): 
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        #self.setWindowTitle("Voltage") 
        self.setWindowTitle("Temperature")                                     #name the window 
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.login_widget = LoginWidget(self)
        self.login_widget.button.clicked.connect(self.plotter)              #connects generated button to desired fucntion. button: "Start Plotting" Conects to fucntion " Plotter"
        self.login_widget.button1.clicked.connect(self.stop)                #connects generated button to desired fucntion  " "
        self.login_widget.button2.clicked.connect(self.clear)               #connects generated button to desired fucntion  " "
        #self.login_widget.button3.clicked.connect(self.save)
        self.central_widget.addWidget(self.login_widget)


        # DO NOT EDIT creates shortcut to kill program and action to be performed in file menu. 
        extractAction = QAction("Exit",self)
        extractAction.setShortcut("Ctrl+Q")
        extractAction.setStatusTip("Leave the App")
        extractAction.triggered.connect(self.close_application)

        # DO NOT EDIT. This Creates the save buttton under file at the top. 

        SaveAction = QAction("Save",self)
        SaveAction.setShortcut("Ctrl+S")
        SaveAction.setStatusTip("Save File")
        SaveAction.triggered.connect(self.save_file)


        # This creates a file menu at the top of the program. You can add " actions" to the menu in the same manner as above. 
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("&File")
        fileMenu.addAction(extractAction) # adds quit option to file menu
        fileMenu.addAction(SaveAction)    # adds save option to file me 

        
    def plotter(self):
        self.data =[0]
        self.temperature = [0]  #UNCOMMENT TO READ BUILT IN TEMPERATURE SENSOR
        #self.Volts = [0]        #  creates array so that the voltage can be stored. 
        self.times = [0]        # an array to store real time. ( starts when plotting beings.)
        self.dat = [0]

        # DO NOT EDIT. This creates the timer that controls how fast the plot updates. Not to be confused with sample rate. 
        self.curve = self.login_widget.plot.getPlotItem().plot()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updater)
        self.timer.start(0)                             # Updates plot every 1ms.

        # DO NOT EDIT
        self.time = QElapsedTimer()                     # Creates times to track how long the plotter is recording data.
                                                        # starts as soon as the button " Start" is clicked. Will resest upon stopping the plot. 
        self.time.start()
        
     
        
    def updater(self):
        
    
        self.temp1 = d.getTemperature()
        
        #self.volt1 = d.getAIN(30)                         # reads voltage off of analog input. The number changes based on what i/o your using on the labjack
        #self.Volts.append(self.volt1)
        self.temp = (self.temp1-273.15)*1.8 +32          # convert to F...... UNCOMMENT TO USE BUILT IN TEMPERATURE SENSOR
        
        self.temperature.append( self.temp )             # UNCOMMENT TO USE BUILT IN TEMPERATURE SENSOR
        self.times.append(self.time.elapsed()/1000)       # Converts time to secoonds and stores the data in the array "times". 

        self.curve.setData(self.times,self.temperature)  # UNCOMMENT TO USE BUILT IN TEMPERATURE SENSOR 

        #self.curve.setData(self.times,self.Volts)         # This tells pyQt what to plot.  

        
    def stop(self):

        self.timer.stop() # stops the plot upon clicking "Stop" 
    
        
       
    # Clears all data from the plot and the data arrays. 
    def clear(self):
        self.curve.clear() 
        
    # DO NOT EDIT!!!!! This gives the option to save the data as any name you would like. 
    def save_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        file = open(fileName, 'w')
        data = np.vstack((self.times,self.temperature)).T     # UNCOMMENT TO USE BUILT IN TEMPERATURE SENSOR 
       # data = np.vstack((self.times,self.Volts)).T            # Creates 2D array from desired data. 
        data1 = str(data)                                      # Can only write strings
        file.write(data1)
        file.close()

    def close_application(self):
        sys.exit()

        #this section physically creates the widets. Here, you can chage the axis labels, and physically add buttons to the GUI.
class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super(LoginWidget, self).__init__(parent)
        # define plot axis(s)
        self.plot = pg.PlotWidget()
        self.plot.setLabel('bottom','Time', 's')
        self.plot.setLabel('left','Temperature','F')
        #self.plot.setLabel('left','Voltage','V')
        self.plot.showGrid(x=True, y=True)
        

        self.button = QPushButton('Start Plotting') # creates button named "Start Plotting" 
        self.button1 = QPushButton('Stop Plotting')
        self.button2 = QPushButton("Clear Plot")
        
        layout = QHBoxLayout() #sets first layout (the plot) to a horizontal orientation with respect to layout 2 (the buttons)
        layout2 = QVBoxLayout() # makes each button vertically aligned with one another. 
      

        # this physically adds the buttons with the desired layout to the GUI.   
        layout2.addWidget(self.button)
        layout2.addWidget(self.button1)
        layout2.addWidget(self.button2)
        layout.addWidget(self.plot)

        layout.addLayout(layout2)
    
        self.setLayout(layout)
        

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()