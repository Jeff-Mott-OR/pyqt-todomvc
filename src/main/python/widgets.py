from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyleFactory,
    QVBoxLayout,
    QWidget
)

from appState import AppState, Filter, todosFiltered

def guiStyleMenuActions(appState: AppState):
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

def todoLineEditWidget(appState: AppState):
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

def markAllWidget(appState: AppState):
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

def todoLineEditMarkAllWidget(appState: AppState):
    widget = QWidget()
    layout = QHBoxLayout(widget)

    layout.addWidget(markAllWidget(appState))
    layout.addSpacing(10)
    layout.addWidget(todoLineEditWidget(appState))

    return widget

def todoListWidget(appState: AppState):
    def renderTodoList():
        todosWidget = QWidget()
        todosLayout = QVBoxLayout(todosWidget)

        for todo in todosFiltered(appState):
            def loopClosureCapture():
                todoClosureCapture = todo

                todoCheckBox = QCheckBox()
                todoCheckBox.setChecked(todo.done)
                todoCheckBox.toggled.connect(lambda checked: appState.setTodosDone([todoClosureCapture], checked))

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
                        appState.setTodoText(todoClosureCapture, text)
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

def numRemainingLabel(appState: AppState):
    def itemsRemainingText():
        todosNotDone = [todo for todo in appState.todos() if not todo.done]
        maybePlural = "s" if len(todosNotDone) != 1 else ""
        return f"{len(todosNotDone)} item{maybePlural} left!"

    widget = QLabel(itemsRemainingText())

    appState.events.on("todosChange", lambda: widget.setText(itemsRemainingText()))

    return widget

def todosFilterBox(appState: AppState):
    groupBox = QGroupBox()
    layout = QHBoxLayout(groupBox)

    for filterLabel in [(Filter.ALL, "All"), (Filter.ACTIVE, "Active"), (Filter.COMPLETED, "Completed")]:
        def loopClosureCapture():
            filterKeyClosureCapture = filterLabel[0]

            button = QPushButton(filterLabel[1])
            button.setCheckable(True)
            button.setFlat(True)

            def updateCheckedState():
                button.setChecked(appState.todosFilter() == filterKeyClosureCapture)
            updateCheckedState() # Render initial state.

            button.clicked.connect(lambda: appState.setTodosFilter(filterKeyClosureCapture))
            appState.events.on("filterChange", updateCheckedState)

            layout.addWidget(button)
        loopClosureCapture()

    return groupBox

def clearCompletedButton(appState: AppState):
    button = QPushButton("Clear Completed")
    button.clicked.connect(lambda: appState.deleteTodosDone())

    return button

def footerWidget(appState: AppState):
    widget = QWidget()
    layout = QHBoxLayout(widget)

    layout.addWidget(numRemainingLabel(appState))
    layout.addStretch()
    layout.addWidget(todosFilterBox(appState))
    layout.addStretch()
    layout.addWidget(clearCompletedButton(appState))

    def updateFooterVisible():
        widget.setVisible(len(appState.todos()) > 0)
    updateFooterVisible() # Render initial state.

    appState.events.on("todosChange", updateFooterVisible)

    return widget

def todoBox(appState: AppState):
    groupBox = QGroupBox("Todos")
    layout = QVBoxLayout(groupBox)

    layout.addWidget(todoLineEditMarkAllWidget(appState))
    layout.addWidget(todoListWidget(appState))
    layout.addStretch()
    layout.addWidget(footerWidget(appState))

    # Give the group box some breathing room.
    # Maybe there's margins or spacing that would accomplish the same?
    wrapWidget = QWidget()
    wrapLayout = QVBoxLayout(wrapWidget)
    wrapLayout.addWidget(groupBox)

    return wrapWidget
