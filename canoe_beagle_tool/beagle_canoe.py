# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'beagle_canoe.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.PB_StartBeagle = QtWidgets.QPushButton(self.centralwidget)
        self.PB_StartBeagle.setGeometry(QtCore.QRect(170, 10, 75, 23))
        self.PB_StartBeagle.setObjectName("PB_StartBeagle")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(670, 20, 104, 231))
        self.textEdit.setObjectName("textEdit")
        self.PB_StartCANoe = QtWidgets.QPushButton(self.centralwidget)
        self.PB_StartCANoe.setGeometry(QtCore.QRect(170, 110, 75, 23))
        self.PB_StartCANoe.setObjectName("PB_StartCANoe")
        self.PB_OpenCANoe = QtWidgets.QPushButton(self.centralwidget)
        self.PB_OpenCANoe.setGeometry(QtCore.QRect(60, 110, 75, 23))
        self.PB_OpenCANoe.setObjectName("PB_OpenCANoe")
        self.lineEdit_SPI_Id = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_SPI_Id.setGeometry(QtCore.QRect(60, 180, 113, 20))
        self.lineEdit_SPI_Id.setObjectName("lineEdit_SPI_Id")
        self.PB_CANoeFDX = QtWidgets.QPushButton(self.centralwidget)
        self.PB_CANoeFDX.setGeometry(QtCore.QRect(60, 10, 75, 23))
        self.PB_CANoeFDX.setObjectName("PB_CANoeFDX")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.PB_StartBeagle.setText(_translate("MainWindow", "Start_beagle"))
        self.PB_StartCANoe.setText(_translate("MainWindow", "StartCANoe"))
        self.PB_OpenCANoe.setText(_translate("MainWindow", "OpenCANoe"))
        self.PB_CANoeFDX.setText(_translate("MainWindow", "CANoeFDX"))
