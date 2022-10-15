"""
Test cases for Inventory Model

"""
import os
import logging
import unittest
from service import app
from service.models import Inventory, DataValidationError, db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Inventory   M O D E L   T E S T   C A S E S
######################################################################
class TestInventory(unittest.TestCase):
    """ Test Cases for Inventory Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Inventory.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_inventory_record(self):
        inventory_records = Inventory.all()
        self.assertEqual(inventory_records, [])

        record = Inventory(name="monitor", condition=Inventory.Condition.NEW, quantity=10, reorder_quantity=20, restock_level=2)
        self.assertTrue(record is not None)
        self.assertEqual(str(record), "<Inventory %r id=[%s]>" % ("monitor", "None"))
        self.assertEqual(record.id, None)
        self.assertEqual(record.name, "monitor")
        self.assertEqual(record.condition, Inventory.Condition.NEW)
        self.assertEqual(record.quantity, 10)
        self.assertEqual(record.reorder_quantity, 20)
        self.assertEqual(record.restock_level, 2)

    def test_inventory_serialize(self):
        record = Inventory(id=1, name="monitor", condition=Inventory.Condition.NEW, quantity=10, reorder_quantity=20, restock_level=2)
        actual_output = record.serialize()
        expected_output = {
            "id": 1,
            "name": "monitor",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
        }
        self.assertEqual(actual_output, expected_output)

    def test_inventory_deserialize(self):
        data = {
            "id": 1,
            "name": "monitor",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
        }
        record = Inventory()
        record.deserialize(data)
        self.assertEqual(record.id, 1)
        self.assertEqual(record.name, "monitor")
        self.assertEqual(record.condition, Inventory.Condition.NEW)
        self.assertEqual(record.quantity, 10)
        self.assertEqual(record.reorder_quantity, 20)
        self.assertEqual(record.restock_level, 2)

    def test_invalid_inventory_deserialize(self):
        data = {}
        record = Inventory()
        self.assertRaises(DataValidationError, record.deserialize, data)
