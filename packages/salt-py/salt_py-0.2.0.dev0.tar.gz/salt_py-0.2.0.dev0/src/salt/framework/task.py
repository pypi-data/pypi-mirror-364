from typing import Callable


class TaskWrapper:
    def __init__(self, name: str, func: Callable, owner: "Workflow"):
        self.name = name
        self.func = func
        self.owner = owner

    def __call__(self):
        return self.func()

    def __rshift__(self, other: "TaskWrapper"):
        self.owner.add_dependency(self.name, other.name)
        return other


def task(func: Callable):
    func._is_task = True
    return func
