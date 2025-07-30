import random
from abc import ABC, abstractmethod
from collections import deque


class Player(ABC):
    def __init__(self, name: str, action=None) -> None:
        self.name = name
        self.action = action

    @abstractmethod
    def choose_action(self, action_count: int) -> int:
        pass


class FixedActionPlayer(Player):
    def __init__(
        self,
        name: str,
        action: int | deque,
        is_cycle: bool | None = None,
    ) -> None:
        super().__init__(name)
        if isinstance(action, int):
            self.action = action
            self.action_queue = None
            self.original_queue = None
            self.is_cycle = None
            self.set_action = None
            self.type = "fixed"
        elif isinstance(action, deque):
            self.action_queue = deque(action)
            self.original_queue = (
                deque(action) if is_cycle else None
            )  # to copy when action_queue is empty
            self.is_cycle = is_cycle
            self.type = "fixed_queue"

    def choose_action(self, action_count: int) -> int:
        if self.action_queue is not None:
            if self.action_queue:
                return self.action_queue.popleft()
            elif self.is_cycle and self.original_queue:  # reset
                self.action_queue = self.original_queue.copy()
                return self.action_queue.popleft()
            else:
                raise ValueError("Action queue is empty")
        else:
            return self.action


class RandomActionPlayer(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.action = None
        self.type = "random"

    def choose_action(self, action_count: int) -> int:
        self.action = random.randrange(0, action_count)
        return self.action
