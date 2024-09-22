from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow

from appState import AppState
from widgets import guiStyleMenuActions, todoBox

appCtxt = ApplicationContext()
appState = AppState(appCtxt.app)
window = QMainWindow()
window.setWindowTitle("PyQt TodoMVC")
window.resize(640, 480);

piMenu = window.menuBar().addMenu("π")
for menuAction in guiStyleMenuActions(appState):
    piMenu.addAction(menuAction)

window.setCentralWidget(todoBox(appState))

window.show()
appCtxt.app.exec()
