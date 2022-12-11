"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from service.models import Inventory


class InventoryFactory(factory.Factory):
    """Creates fake records for testing purposes"""
    
    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""
        model = Inventory

    # FuzzyInteger will return random numbers between 0 to 2147483648
    product_id = FuzzyInteger(2147483648)
    name = FuzzyChoice(choices=["laptop", "monitor", "desk", "chair"])
    condition = FuzzyChoice(choices=[Inventory.Condition.NEW, Inventory.Condition.REFURBISHED, Inventory.Condition.RETURN])
    quantity = FuzzyChoice(choices=[10, 15, 20])
    reorder_quantity = FuzzyChoice(choices=[10, 15, 20])
    restock_level = FuzzyChoice(choices=[1, 2, 3])
    active = FuzzyChoice(choices=[True, False])
