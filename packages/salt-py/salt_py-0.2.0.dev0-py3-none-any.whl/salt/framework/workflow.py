import inspect
from salt.framework.task import TaskWrapper

from typing import Dict, List, Set, Callable


class Workflow:
    def __init__(self):
        self._functions: Dict[str, Callable] = {}
        self.tasks: Dict[str, TaskWrapper] = {}
        self.dependencies: Dict[str, Set[str]] = {}

        self._register_tasks()
        self.graph()

    def _register_tasks(self):
        for name, member in inspect.getmembers(self, predicate=inspect.ismethod):
            if getattr(member, "_is_task", False):
                self._functions[name] = member
                self.tasks[name] = TaskWrapper(name, member, self)
                self.dependencies[name] = set()
                setattr(self, name, self.tasks[name])  # override method with wrapper

    def add_dependency(self, from_task: str, to_task: str):
        if from_task not in self.tasks or to_task not in self.tasks:
            raise ValueError(f"Invalid dependency: {from_task} -> {to_task}")
        self.dependencies[to_task].add(from_task)

    def graph(self):
        """Re-implement this function using shift operators to define order of task execution and dependencies."""
        raise NotImplementedError("Subclasses must implement graph()")

    def get_ordered_tasks(self) -> List[str]:
        visited = set()
        stack = []

        def visit(node):
            if node in visited:
                return
            visited.add(node)
            for dep in self.dependencies.get(node, []):
                visit(dep)
            stack.append(node)

        for task in self.tasks:
            visit(task)
        return stack

    def run(self):
        for task_name in self.get_ordered_tasks():
            print(f"Running task: {task_name}")
            self.tasks[task_name]()
