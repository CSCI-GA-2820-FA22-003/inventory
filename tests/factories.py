"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Inventory


class InventoryFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    name = FuzzyChoice(choices=["laptop", "monitor", "desk", "chair"])
    condiiton = FuzzyChoice(choices=[Inventory.condition.NEW, Inventory.condition.REFURBISHED, Inventory.condition.NEW])
    quantity = FuzzyChoice(choices=[10, 15, 20])
    reorder_quantity = FuzzyChoice(choices=[10, 15, 20])
    restock_level = FuzzyChoice(choices=[1, 2, 3])
