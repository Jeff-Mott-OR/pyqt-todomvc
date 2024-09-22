from typing import List

from event_emitter import EventEmitter
from PyQt5.QtWidgets import QApplication

# Just a struct.
class Todo:
    def __init__(self, text: str, done: bool = False):
        self.text = text
        self.done = done
        self.editing = False

class Filter:
    ALL = 1
    ACTIVE = 2
    COMPLETED = 3

# This app state represents the one source for truth. UI interactions should
# update the app state, then the app state will notify subscribers to update
# themselves.
class AppState:
    def __init__(self, qApp: QApplication):
        self.events = EventEmitter()

        self._todos = []
        self._todosFilter = Filter.ALL
        self._qApp = qApp

    def addTodo(self, text: str):
        self._todos.append(Todo(text))
        self.events.emit("todosChange")

    def todos(self):
        return self._todos

    def setTodoText(self, todo: Todo, text: str):
        todo.text = text
        todo.editing = False
        self.events.emit("todosChange")

    def setTodoEditing(self, todo: Todo):
        todo.editing = True
        self.events.emit("todosChange")

    def setTodosDone(self, todos: List[Todo], done: bool):
        for todo in todos:
            todo.done = done
        self.events.emit("todosChange")

    def deleteTodo(self, removeTodo: Todo):
        self._todos = [todo for todo in self._todos if not todo is removeTodo]
        self.events.emit("todosChange")

    def deleteTodosDone(self):
        self._todos = [todo for todo in self._todos if not todo.done]
        self.events.emit("todosChange")

    def setTodosFilter(self, filter: Filter):
        self._todosFilter = filter
        self.events.emit("filterChange")

    def todosFilter(self):
        return self._todosFilter

    # Style name should be one of the keys returned from `QStyleFactory.keys()`.
    def setGuiStyle(self, styleName: str):
        self._qApp.setStyle(styleName)
        self.events.emit("guiStyleChange")

    def guiStyle(self):
        return self._qApp.style().objectName()

# This function can be implemented without access to any of the private state.
# Since it doesn't need access to privates, it doesn't need to be a method in the class.
def todosFiltered(appState):
    filter = appState.todosFilter()
    for todo in appState.todos():
        if (
            filter == Filter.ALL
            or filter == Filter.ACTIVE and not todo.done
            or filter == Filter.COMPLETED and todo.done
        ):
            yield todo
