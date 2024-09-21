from fbs_runtime.application_context.PyQt5 import ApplicationContext

from event_emitter import EventEmitter
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStyleFactory,
    QVBoxLayout,
    QWidget
)

# Basically just a struct.
class Todo:
    def __init__(self, text, done = False):
        self.text = text
        self.done = done

# This app state represents the one source for truth.
# UI interactions should update the app state,
# then the app state will notify subscribers to update themselves.
class AppState:
    def __init__(self, qApp):
        self.events = EventEmitter()

        self._todos = []
        self._todosFilter = "all" # all | active | completed
        self._qApp = qApp

    def todos(self):
        # Consider returning a shallow copy to enforce read-only. But for now keep it simple.
        return self._todos
    def addTodo(self, text):
        self._todos.append(Todo(text))
        self.events.emit("todosChange")
    def setTodoDone(self, todo, done):
        todo.done = done
        self.events.emit("todosChange")
    def setAllTodosDone(self, done):
        for todo in self._todos:
            todo.done = done
        self.events.emit("todosChange")
    def deleteTodo(self, removeTodo):
        self._todos = [todo for todo in self._todos if not todo is removeTodo]
        self.events.emit("todosChange")
    def clearTodosDone(self):
        self._todos = [todo for todo in self._todos if not todo.done]
        self.events.emit("todosChange")

    def todosFilter(self):
        return self._todosFilter
    def setTodosFilter(self, filter):
        self._todosFilter = filter
        self.events.emit("filterChange")

    def guiStyle(self):
        return self._qApp.style().objectName()
    def setGuiStyle(self, styleName):
        self._qApp.setStyle(styleName)
        self.events.emit("guiStyleChange")

def guiStyleMenuActions():
    for styleKey in QStyleFactory.keys():
        def loopClosureCapture():
            # The loop varialbe `styleKey` will change value next loop iteration,
            # so we need to use a closure to capture a per-iteration copy.
            styleKeyClosureCapture = styleKey

            menuAction = QAction(f"{styleKey} style")
            menuAction.setCheckable(True)

            def updateCheckedState():
                menuAction.setChecked(appState.guiStyle() == styleKeyClosureCapture.lower())
            updateCheckedState() # Render initial state.

            # When a menu is clicked, update the one source for truth.
            menuAction.triggered.connect(lambda: appState.setGuiStyle(styleKeyClosureCapture))
            # After the one source for truth is updated, it will notify all interested parties.
            appState.events.on("guiStyleChange", updateCheckedState)

            return menuAction
        yield loopClosureCapture()

def todoLineEditWidget():
    lineEdit = QLineEdit()
    lineEdit.setPlaceholderText("What needs to be done?")

    def onReturnPressed():
        text = lineEdit.text().strip()
        if not text:
            return
        appState.addTodo(text)
        lineEdit.clear()

    lineEdit.returnPressed.connect(onReturnPressed)

    return lineEdit

def markAllWidget():
    checkBox = QCheckBox()
    checkBox.setToolTip("Mark all")
    checkBox.setTristate(True)

    def updateCheckedState():
        anyDone = any(todo.done for todo in appState.todos())
        anyNotDone = any(not todo.done for todo in appState.todos())

        checkBox.setCheckState(
            Qt.CheckState.PartiallyChecked if anyDone and anyNotDone
            else Qt.CheckState.Checked if anyDone else Qt.CheckState.Unchecked
        )
    updateCheckedState() # Render initial state.

    checkBox.released.connect(lambda: appState.setAllTodosDone(checkBox.isChecked()))
    appState.events.on("todosChange", updateCheckedState)

    return checkBox

def todoLineEditMarkAllWidget():
    widget = QWidget()
    layout = QHBoxLayout(widget)

    layout.addWidget(markAllWidget())
    layout.addSpacing(10)
    layout.addWidget(todoLineEditWidget())

    return widget

def todoListWidget():
    def renderTodoList():
        todosWidget = QWidget()
        todosLayout = QVBoxLayout(todosWidget)

        todosFiltered = [
            todo
                for todo in appState.todos()
                if
                    appState.todosFilter() == "all" or
                    appState.todosFilter() == "active" and not todo.done or
                    appState.todosFilter() == "completed" and todo.done
        ]

        for todo in todosFiltered:
            def loopClosureCapture():
                todoClosureCapture = todo

                todoCheckBox = QCheckBox(todo.text)
                if todo.done:
                    todoCheckBox.setChecked(True)

                    font = todoCheckBox.font()
                    font.setStrikeOut(True)
                    todoCheckBox.setFont(font)
                todoCheckBox.toggled.connect(lambda checked: appState.setTodoDone(todoClosureCapture, checked))

                closeButton = QPushButton("╳")
                closeButton.setToolTip("Delete entry")
                closeButton.clicked.connect(lambda: appState.deleteTodo(todoClosureCapture))

                todoRowLayout = QHBoxLayout()
                todoRowLayout.addWidget(todoCheckBox)
                todoRowLayout.addStretch()
                todoRowLayout.addWidget(closeButton)

                todosLayout.addLayout(todoRowLayout)
            loopClosureCapture()

        return todosWidget

    widget = renderTodoList() # Render initial state.

    def updateTodoList():
        nonlocal widget

        oldWidget = widget
        widget = renderTodoList()
        oldWidget.parentWidget().layout().replaceWidget(oldWidget, widget)

        # Bug in PyQt? oldWidget should be removed entirely,
        # and yet I'll still see it unless I hide it.
        oldWidget.hide()

    appState.events.on("todosChange", updateTodoList)
    appState.events.on("filterChange", updateTodoList)

    return widget

def numRemainingLabel():
    def itemsRemainingText():
        todosNotDone = [todo for todo in appState.todos() if not todo.done]
        maybePlural = "s" if len(todosNotDone) != 1 else ""
        return f"{len(todosNotDone)} item{maybePlural} left!"

    widget = QLabel(itemsRemainingText())

    appState.events.on("todosChange", lambda: widget.setText(itemsRemainingText()))

    return widget

def todosFilterBox():
    groupBox = QGroupBox()
    layout = QHBoxLayout(groupBox)

    for filterLabel in ["All", "Active", "Completed"]:
        def loopClosureCapture():
            filterKeyClosureCapture = filterLabel.lower()

            button = QPushButton(filterLabel)
            button.setCheckable(True)
            button.setFlat(True)

            def updateCheckedState():
                button.setChecked(appState.todosFilter() == filterKeyClosureCapture)
            updateCheckedState() # Render initial state.

            button.released.connect(lambda: appState.setTodosFilter(filterKeyClosureCapture))
            appState.events.on("filterChange", updateCheckedState)

            layout.addWidget(button)
        loopClosureCapture()

    return groupBox

def clearCompletedButton():
    button = QPushButton("Clear Completed")
    button.released.connect(lambda: appState.clearTodosDone())

    return button

def footerWidget():
    widget = QWidget()
    layout = QHBoxLayout(widget)

    layout.addWidget(numRemainingLabel())
    layout.addStretch()
    layout.addWidget(todosFilterBox())
    layout.addStretch()
    layout.addWidget(clearCompletedButton())

    def updateFooterVisible():
        widget.setVisible(len(appState.todos()) > 0)
    updateFooterVisible() # Render initial state.

    appState.events.on("todosChange", updateFooterVisible)

    return widget

def todoBox():
    groupBox = QGroupBox("Todos")
    layout = QVBoxLayout(groupBox)

    layout.addWidget(todoLineEditMarkAllWidget())
    layout.addWidget(todoListWidget())
    layout.addStretch()
    layout.addWidget(footerWidget())

    # Give the group box some breathing room.
    # Maybe there's margins or spacing that would accomplish the same?
    wrapWidget = QWidget()
    wrapLayout = QVBoxLayout(wrapWidget)
    wrapLayout.addWidget(groupBox)

    return wrapWidget

appCtxt = ApplicationContext()
appState = AppState(appCtxt.app)
window = QMainWindow()
window.setWindowTitle("PyQt TodoMVC")
window.resize(640, 480);

piMenu = window.menuBar().addMenu("π")
for menuAction in guiStyleMenuActions():
    piMenu.addAction(menuAction)

window.setCentralWidget(todoBox())

window.show()
appCtxt.app.exec()
