from PyQt5 import QtCore, QtGui, QtWidgets

buttonWidth = 120
rightHeight = 110
dialAngle = 0
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet("background-color: #232323;")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.mainLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # LEFT NAVBAR
        self.navbarWidget = QtWidgets.QWidget(self.centralwidget)
        self.navbarWidget.setFixedWidth(buttonWidth + 20)
        self.navbarWidget.setStyleSheet("background-color: #181818;")
        self.navbarLayout = QtWidgets.QVBoxLayout(self.navbarWidget)
        self.navbarLayout.setContentsMargins(10, 10, 10, 10)
        self.navbarLayout.setSpacing(12)

        self.pushButton = QtWidgets.QPushButton()
        self.pushButton.setFixedWidth(buttonWidth)
        self.pushButton.setFixedHeight(100)
        self.pushButton.setStyleSheet("""
            QPushButton {
                background-color: #181818;
                border-style: solid;
                border-width: 2px;
                border-color: #181818;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                border-color: white;
                color: white;
            }
        """)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("C:/Users/XBbur/OneDrive/Desktop/SPARK/uielements/home_icon_off.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap("C:/Users/XBbur/OneDrive/Desktop/SPARK/uielements/home_icon_ON.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(74, 74))
        self.navbarLayout.addWidget(self.pushButton)

        self.pushButton_3 = QtWidgets.QPushButton()
        self.pushButton_3.setFixedWidth(buttonWidth)
        self.pushButton_3.setFixedHeight(100)
        self.pushButton_3.setStyleSheet(self.pushButton.styleSheet())
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("C:/Users/XBbur/OneDrive/Desktop/SPARK/uielements/camera_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_3.setIcon(icon1)
        self.pushButton_3.setIconSize(QtCore.QSize(64, 64))
        self.navbarLayout.addWidget(self.pushButton_3)

        self.pushButton_2 = QtWidgets.QPushButton()
        self.pushButton_2.setFixedWidth(buttonWidth)
        self.pushButton_2.setFixedHeight(100)
        self.pushButton_2.setStyleSheet(self.pushButton.styleSheet())
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("C:/Users/XBbur/OneDrive/Desktop/SPARK/uielements/drone_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon2)
        self.pushButton_2.setIconSize(QtCore.QSize(78, 78))
        self.navbarLayout.addWidget(self.pushButton_2)
    
        self.navbarLayout.addStretch()
        self.mainLayout.addWidget(self.navbarWidget)

        # RIGHT SIDE
        self.rightWidget = QtWidgets.QWidget(self.centralwidget)
        self.rightLayout = QtWidgets.QVBoxLayout(self.rightWidget)
        self.rightLayout.setContentsMargins(10, 10, 10, 10)
        self.rightLayout.setSpacing(10)

        self.mapHolder = QtWidgets.QWidget(self.rightWidget)
        self.mapHolder.setObjectName("mapHolder")
        self.mapHolder.setStyleSheet("background-color: #222; border-radius: 12px;")
        self.mapHolder.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.rightLayout.addWidget(self.mapHolder)

        self.controlsWidget = QtWidgets.QWidget(self.rightWidget)
        self.controlsWidget.setFixedHeight(220)
        self.controlsLayout = QtWidgets.QHBoxLayout(self.controlsWidget)
        self.controlsLayout.setContentsMargins(0, 0, 0, 0)
        self.controlsLayout.setSpacing(20)

        self.compassWidget = QtWidgets.QWidget(self.controlsWidget)
        self.compassLayout = QtWidgets.QVBoxLayout(self.compassWidget)
        self.compassLayout.setContentsMargins(0, 0, 0, 0)
        self.compassLayout.setSpacing(5)

        self.label_title = QtWidgets.QLabel("Camera Direction:")
        self.label_title.setStyleSheet("color: white; font-size: 12pt;")
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.compassLayout.addWidget(self.label_title)

        self.dial = QtWidgets.QDial()
        self.dial.setWrapping(True)
        self.dial.setMinimum(0)
        self.dial.setMaximum(359)
        self.dial.setNotchesVisible(True)
        self.dial.setFixedSize(100, 100)

        self.compassGrid = QtWidgets.QGridLayout()
        self.compassGrid.setHorizontalSpacing(0)
        self.compassGrid.setVerticalSpacing(8)
        self.compassGrid.setContentsMargins(0, 0, 0, 0)

        self.label_n = QtWidgets.QLabel("N")
        self.label_s = QtWidgets.QLabel("S")
        self.label_e = QtWidgets.QLabel("E")
        self.label_w = QtWidgets.QLabel("W")

        for lbl in [self.label_n, self.label_s, self.label_e, self.label_w]:
            lbl.setStyleSheet("color: white; font-size: 10pt;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)

        self.compassGrid.addWidget(self.label_n, 0, 1)
        self.compassGrid.addWidget(self.label_w, 1, 0)
        self.compassGrid.addWidget(self.dial, 1, 1)
        self.compassGrid.addWidget(self.label_e, 1, 2)
        self.compassGrid.addWidget(self.label_s, 2, 1)

        self.compassLayout.addLayout(self.compassGrid)
        self.controlsLayout.addWidget(self.compassWidget)

        self.plusWidget = QtWidgets.QWidget(self.controlsWidget)
        self.controlsLayout.addWidget(self.plusWidget, alignment=QtCore.Qt.AlignCenter)
        self.plusLayout = QtWidgets.QVBoxLayout(self.plusWidget)
        self.plusLayout.setContentsMargins(0, 25, 40, 0)
        self.plusLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.plusLayout.setSpacing(20)

        self.plusButton = QtWidgets.QPushButton("+")
        self.plusButton.setFixedSize(90, 90)
        self.plusButton.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                font-size: 36pt;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)

        self.addCameraLabel = QtWidgets.QLabel("Add Camera:")
        self.addCameraLabel.setStyleSheet("color: white; font-size: 12pt;")
        self.addCameraLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.plusLayout.addWidget(self.addCameraLabel)

        self.cameraNameInput = QtWidgets.QLineEdit()
        self.cameraNameInput.setPlaceholderText("Camera name")
        self.cameraNameInput.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                font-size: 12pt;
                padding: 5px;
                border-radius: 5px;
            }
        """)
        self.cameraNameInput.setFixedWidth(140)
        self.plusLayout.addWidget(self.cameraNameInput, alignment=QtCore.Qt.AlignCenter)

        self.plusLayout.addWidget(self.plusButton, alignment=QtCore.Qt.AlignCenter)


        self.controlsLayout.addWidget(self.plusWidget)
        self.rightLayout.addWidget(self.controlsWidget)

        self.mainLayout.addWidget(self.rightWidget)
        MainWindow.setCentralWidget(self.centralwidget)

     #   self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.plusButton.clicked.connect(self.place_pin_on_click)

    def place_pin_on_click(self):
        print("Add Camera button clicked!")
        angle = self.get_dial_angle()
        print(angle)

    def get_dial_angle(self):
        return self.ui.dial.value()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
