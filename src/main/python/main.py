from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PyQt5 import ApplicationContext

import random
import sys

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QMainWindow, QMenu, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QToolBar, QVBoxLayout, QWidget)

STYLE_KEYS = QStyleFactory.keys()
ORIGINAL_PALETTE = QApplication.palette()

# Think of this like an object literal. That's why it's named in lower camel case.
# It is inspired by React/Redux. This app state is the one source for truth,
# and the methods are actions to update the state and update the UI widgets.
class appState:
    styleKey = random.choice(STYLE_KEYS)
    useStylePalette = random.choice([True, False])
    disableWidgets = random.choice([True, False])
    progressPercent = 13

    @classmethod
    def changeStyle(self, styleKey):
        self.styleKey = styleKey
        QApplication.setStyle(QStyleFactory.create(styleKey))
        self._updatePalette()

    @classmethod
    def changePalette(self, useStylePalette):
        self.useStylePalette = useStylePalette
        self._updatePalette()

    @classmethod
    def _updatePalette(self):
        if (self.useStylePalette):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(ORIGINAL_PALETTE)

    @classmethod
    def changeDisableWidgets(self, disableWidgets):
        self.disableWidgets = disableWidgets

        disableWidgetsCheckBox.setChecked(disableWidgets)
        disableWidgetsMenuAction.setChecked(disableWidgets)

        topLeftGroupBox.setDisabled(disableWidgets)
        topRightGroupBox.setDisabled(disableWidgets)
        bottomLeftTabWidget.setDisabled(disableWidgets)
        bottomRightGroupBox.setDisabled(disableWidgets)

    @classmethod
    def changeProgress(self, progressPercent):
        self.progressPercent = progressPercent % 101
        progressBar.setValue(progressBar.maximum() * self.progressPercent // 100)

# An ApplicationContext that passes argv to the underlying QApplication.
# More: https://build-system.fman.io/manual/#ApplicationContext
class ApplicationContextArgv(ApplicationContext):
    @cached_property
    def app(self):
        return QApplication(sys.argv)

appctxt = ApplicationContextArgv()
QApplication.setStyle(QStyleFactory.create(appState.styleKey))
if (appState.useStylePalette):
    QApplication.setPalette(QApplication.style().standardPalette())

def createTopLayout():
    topLayout = QHBoxLayout()

    styleComboBox = QComboBox()
    styleComboBox.addItems(STYLE_KEYS)
    styleComboBox.setCurrentText(appState.styleKey)
    styleComboBox.textActivated.connect(lambda styleKey: appState.changeStyle(styleKey))

    styleLabel = QLabel("&Style:")
    styleLabel.setBuddy(styleComboBox)
    topLayout.addWidget(styleLabel)
    topLayout.addWidget(styleComboBox)
    topLayout.addStretch(1)

    useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
    useStylePaletteCheckBox.setChecked(appState.useStylePalette)
    useStylePaletteCheckBox.toggled.connect(lambda isChecked: appState.changePalette(isChecked))
    topLayout.addWidget(useStylePaletteCheckBox)

    disableWidgetsCheckBox = QCheckBox("&Disable widgets")
    disableWidgetsCheckBox.setChecked(appState.disableWidgets)
    disableWidgetsCheckBox.toggled.connect(lambda isChecked: appState.changeDisableWidgets(isChecked))
    topLayout.addWidget(disableWidgetsCheckBox)

    return (topLayout, disableWidgetsCheckBox)
(topLayout, disableWidgetsCheckBox) = createTopLayout()

def createTopLeftGroupBox():
    topLeftGroupLayout = QVBoxLayout()

    radioButton1 = QRadioButton("Radio button 1")
    radioButton1.setChecked(True)
    topLeftGroupLayout.addWidget(radioButton1)
    topLeftGroupLayout.addWidget(QRadioButton("Radio button 2"))
    topLeftGroupLayout.addWidget(QRadioButton("Radio button 3"))

    checkBox = QCheckBox("Tri-state check box")
    checkBox.setTristate(True)
    checkBox.setCheckState(Qt.CheckState.PartiallyChecked)
    topLeftGroupLayout.addWidget(checkBox)
    topLeftGroupLayout.addStretch(1)

    topLeftGroupBox = QGroupBox("Group 1")
    topLeftGroupBox.setDisabled(appState.disableWidgets)
    topLeftGroupBox.setLayout(topLeftGroupLayout)

    return topLeftGroupBox
topLeftGroupBox = createTopLeftGroupBox()

def createTopRightGroupBox():
    topRightGroupLayout = QVBoxLayout()

    defaultPushButton = QPushButton("Default Push Button")
    defaultPushButton.setDefault(True)
    topRightGroupLayout.addWidget(defaultPushButton)

    togglePushButton = QPushButton("Toggle Push Button")
    togglePushButton.setCheckable(True)
    togglePushButton.setChecked(True)
    topRightGroupLayout.addWidget(togglePushButton)

    flatPushButton = QPushButton("Flat Push Button")
    flatPushButton.setFlat(True)
    topRightGroupLayout.addWidget(flatPushButton)
    topRightGroupLayout.addStretch(1)

    topRightGroupBox = QGroupBox("Group 2")
    topRightGroupBox.setDisabled(appState.disableWidgets)
    topRightGroupBox.setLayout(topRightGroupLayout)

    return topRightGroupBox
topRightGroupBox = createTopRightGroupBox()

def createBottomLeftTabWidget():
    tab1HBox = QHBoxLayout()
    tab1HBox.setContentsMargins(5, 5, 5, 5)
    tab1HBox.addWidget(QTableWidget(10, 10))
    tab1 = QWidget()
    tab1.setLayout(tab1HBox)

    tab2HBox = QHBoxLayout()
    tab2HBox.setContentsMargins(5, 5, 5, 5)
    textEdit = QTextEdit()
    textEdit.setPlainText("Twinkle, twinkle, little star,\n"
                            "How I wonder what you are.\n"
                            "Up above the world so high,\n"
                            "Like a diamond in the sky.\n"
                            "Twinkle, twinkle, little star,\n"
                            "How I wonder what you are!\n")
    tab2HBox.addWidget(textEdit)
    tab2 = QWidget()
    tab2.setLayout(tab2HBox)

    bottomLeftTabWidget = QTabWidget()
    bottomLeftTabWidget.setDisabled(appState.disableWidgets)
    bottomLeftTabWidget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Ignored)
    bottomLeftTabWidget.addTab(tab1, "&Table")
    bottomLeftTabWidget.addTab(tab2, "Text &Edit")

    return bottomLeftTabWidget
bottomLeftTabWidget = createBottomLeftTabWidget()

def createBottomRightGroupBox():
    layout = QGridLayout()

    lineEdit = QLineEdit('s3cRe7')
    lineEdit.setEchoMode(QLineEdit.EchoMode.Password)
    layout.addWidget(lineEdit, 0, 0, 1, 2)

    spinBox = QSpinBox()
    spinBox.setValue(50)
    layout.addWidget(spinBox, 1, 0, 1, 2)

    dateTimeEdit = QDateTimeEdit()
    dateTimeEdit.setDateTime(QDateTime.currentDateTime())
    layout.addWidget(dateTimeEdit, 2, 0, 1, 2)

    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setValue(40)
    layout.addWidget(slider, 3, 0)

    scrollBar = QScrollBar(Qt.Orientation.Horizontal)
    scrollBar.setValue(60)
    layout.addWidget(scrollBar, 4, 0)

    dial = QDial()
    dial.setNotchesVisible(True)
    dial.setValue(30)
    layout.addWidget(dial, 3, 1, 2, 1)
    layout.setRowStretch(5, 1)

    bottomRightGroupBox = QGroupBox("Group 3")
    bottomRightGroupBox.setCheckable(True)
    bottomRightGroupBox.setChecked(True)
    bottomRightGroupBox.setDisabled(appState.disableWidgets)
    bottomRightGroupBox.setLayout(layout)

    return bottomRightGroupBox
bottomRightGroupBox = createBottomRightGroupBox()

def createProgressBar():
    progressBar = QProgressBar()
    progressBar.setRange(0, 10000)
    progressBar.setValue(progressBar.maximum() * appState.progressPercent // 100)

    timer = QTimer(progressBar)
    timer.timeout.connect(lambda: appState.changeProgress(appState.progressPercent + 1))
    timer.start(1000)

    return progressBar
progressBar = createProgressBar()

mainLayout = QGridLayout()
mainLayout.addLayout(topLayout, 0, 0, 1, 2) # row, column, rowSpan, columnSpan
mainLayout.setColumnStretch(0, 1)
mainLayout.addWidget(topLeftGroupBox, 1, 0) # row, column [, rowSpan=1, columnSpan=1]
mainLayout.addWidget(topRightGroupBox, 1, 1)
mainLayout.setRowStretch(1, 1)
mainLayout.setColumnStretch(1, 1)
mainLayout.addWidget(bottomLeftTabWidget, 2, 0)
mainLayout.addWidget(bottomRightGroupBox, 2, 1)
mainLayout.setRowStretch(2, 1)
mainLayout.addWidget(progressBar, 3, 0, 1, 2)

widgetGallery = QWidget()
widgetGallery.setLayout(mainLayout)

window = QMainWindow()
window.setCentralWidget(widgetGallery)
window.setWindowTitle("Styles")

disableWidgetsMenuAction = QAction("&Disable widgets")
disableWidgetsMenuAction.setCheckable(True)
disableWidgetsMenuAction.triggered.connect(lambda isChecked: appState.changeDisableWidgets(isChecked))

menu = window.menuBar().addMenu("π")
menu.addAction(disableWidgetsMenuAction)

window.show()
appctxt.app.exec()
