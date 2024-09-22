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
        self.editing = False

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
    def setTodosDone(self, todos, done):
        for todo in todos:
            todo.done = done
        self.events.emit("todosChange")
    def setTodoEditing(self, todo):
        todo.editing = True
        self.events.emit("todosChange")
    def updateTodo(self, todo, text):
        todo.text = text
        todo.editing = False
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

def todosFiltered(appState):
    filter = appState.todosFilter()
    for todo in appState.todos():
        if filter == "all" or filter == "active" and not todo.done or filter == "completed" and todo.done:
            yield todo

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
        todos = todosFiltered(appState)
        anyDone = any(todo.done for todo in todos)
        anyNotDone = any(not todo.done for todo in todos)

        checkBox.setCheckState(
            Qt.CheckState.PartiallyChecked if anyDone and anyNotDone
            else Qt.CheckState.Checked if anyDone else Qt.CheckState.Unchecked
        )
    updateCheckedState() # Render initial state.

    checkBox.released.connect(lambda: appState.setTodosDone(todosFiltered(appState), checkBox.isChecked()))

    appState.events.on("todosChange", updateCheckedState)
    appState.events.on("filterChange", updateCheckedState)

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

        for todo in todosFiltered(appState):
            def loopClosureCapture():
                todoClosureCapture = todo

                todoCheckBox = QCheckBox()
                todoCheckBox.setChecked(todo.done)
                todoCheckBox.toggled.connect(lambda checked: appState.setTodoDone(todoClosureCapture, checked))

                if not todo.editing:
                    # Inherit to override protected event methods.
                    class TodoLabel(QLabel):
                        def mouseDoubleClickEvent(self, event):
                            appState.setTodoEditing(todoClosureCapture)
                    todoLabel = TodoLabel(todo.text)
                    if todo.done:
                        font = todoLabel.font()
                        font.setStrikeOut(True)
                        todoLabel.setFont(font)
                else:
                    todoEdit = QLineEdit()
                    todoEdit.setText(todo.text)
                    def onReturnPressed():
                        text = todoEdit.text().strip()
                        if not text:
                            return
                        appState.updateTodo(todoClosureCapture, text)
                    todoEdit.returnPressed.connect(onReturnPressed)

                closeButton = QPushButton("✗")
                closeButton.setToolTip("Delete entry")
                closeButton.clicked.connect(lambda: appState.deleteTodo(todoClosureCapture))

                todoRowLayout = QHBoxLayout()
                todoRowLayout.addWidget(todoCheckBox)
                if not todo.editing:
                    todoRowLayout.addWidget(todoLabel)
                    todoRowLayout.addStretch()
                else:
                    todoRowLayout.addWidget(todoEdit)
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
