# src/foodClass.py
from src.thingClass import Thing


class Food(Thing):
    """
    Base class for consumables.
    - weight: varies per instance
    - calories: fixed per subclass (class attribute)
    """

    CALORIES = 0  # subclasses override

    def __init__(self, weight: int):
        super().__init__()
        if weight <= 0:
            raise ValueError("Food weight must be positive")
        self.weight = int(weight)

    @property
    def calories(self) -> int:
        return int(self.__class__.CALORIES)

    def __str__(self):
        return f"{self.__class__.__name__}(w={self.weight}, cal={self.calories})"


class Milk(Food):
    """Drinkable by the Cat."""

    # per spec: calories same for all Milk instances; tweak here to match course notes if needed
    CALORIES = 10


class Sausage(Food):
    """Edible by the Cat (not drinkable)."""

    CALORIES = 20
