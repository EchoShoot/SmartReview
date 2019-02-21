# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UISearch.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(725, 493)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(350, 440, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.wordsTable = QtWidgets.QTableWidget(Dialog)
        self.wordsTable.setGeometry(QtCore.QRect(20, 10, 681, 411))
        self.wordsTable.setColumnCount(2)
        self.wordsTable.setObjectName("wordsTable")
        self.wordsTable.setRowCount(0)
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(250, 440, 181, 23))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.explainLabel = QtWidgets.QLabel(self.layoutWidget)
        self.explainLabel.setObjectName("explainLabel")
        self.horizontalLayout.addWidget(self.explainLabel)
        self.explainEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.explainEdit.setObjectName("explainEdit")
        self.horizontalLayout.addWidget(self.explainEdit)
        self.layoutWidget1 = QtWidgets.QWidget(Dialog)
        self.layoutWidget1.setGeometry(QtCore.QRect(50, 440, 181, 23))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.wordLabel = QtWidgets.QLabel(self.layoutWidget1)
        self.wordLabel.setObjectName("wordLabel")
        self.horizontalLayout_2.addWidget(self.wordLabel)
        self.wordEdit = QtWidgets.QLineEdit(self.layoutWidget1)
        self.wordEdit.setObjectName("wordEdit")
        self.horizontalLayout_2.addWidget(self.wordEdit)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.wordEdit.textChanged['QString'].connect(self.wordsTable.update)
        self.explainEdit.textChanged['QString'].connect(self.wordsTable.update)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "混淆词选取"))
        self.wordsTable.setSortingEnabled(True)
        self.explainLabel.setText(_translate("Dialog", "释义:"))
        self.wordLabel.setText(_translate("Dialog", "单词:"))

