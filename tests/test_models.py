"""
Test cases for Inventory Model

"""
import os
import logging
import unittest
from service import app
from service.models import Inventory, DataValidationError, OutOfRangeError, db
from tests.factories import InventoryFactory

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

    def test_instantiate_inventory_record(self):
        inventory_records = Inventory.all()
        self.assertEqual(inventory_records, [])

        record = Inventory(product_id=1, name="monitor", condition=Inventory.Condition.NEW,
                            quantity=10, reorder_quantity=20, restock_level=2)
        self.assertTrue(record is not None)
        self.assertEqual(str(record), "<Inventory %r product_id=[%d] condition=[%s]>" % 
                                    ("monitor", 1, Inventory.Condition.NEW.name))
        self.assertEqual(record.product_id, 1)
        self.assertEqual(record.name, "monitor")
        self.assertEqual(record.condition, Inventory.Condition.NEW)
        self.assertEqual(record.quantity, 10)
        self.assertEqual(record.reorder_quantity, 20)
        self.assertEqual(record.restock_level, 2)

    def test_inventory_serialize(self):
        record = Inventory(product_id=1, name="monitor", condition=Inventory.Condition.NEW,
                            quantity=10, reorder_quantity=20, restock_level=2, active = True)
        actual_output = record.serialize()
        logging.debug(actual_output)
        expected_output = {
            "product_id": 1,
            "name": "monitor",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2,
            "active": True
        }
        self.assertEqual(actual_output, expected_output)

    def test_inventory_deserialize(self):
        data = {
            "product_id": 1,
            "name": "monitor",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
        }
        record = Inventory()
        record.deserialize(data)
        self.assertEqual(record.product_id, 1)
        self.assertEqual(record.name, "monitor")
        self.assertEqual(record.condition, Inventory.Condition.NEW)
        self.assertEqual(record.quantity, 10)
        self.assertEqual(record.reorder_quantity, 20)
        self.assertEqual(record.restock_level, 2)

    def test_inventory_deserialize_partial_fields(self):
        data = {
            "product_id": 1,
            "condition": Inventory.Condition.RETURN.value
        }
        record = Inventory()
        record.deserialize(data)
        self.assertEqual(record.product_id, 1)
        self.assertEqual(record.condition, Inventory.Condition.RETURN)
        self.assertEqual(record.name, None)
        self.assertEqual(record.quantity, None)
        self.assertEqual(record.reorder_quantity, None)
        self.assertEqual(record.restock_level, None)


    def test_deserialize_missing_data(self):
        """It should not deserialize inventory with missing data"""
        data = {}
        record = Inventory()
        self.assertRaises(DataValidationError, record.deserialize, data)


    def test_deserialize_type_bad_data(self):
        """It should not deserialize inventory with bad data"""
        data = "this is not a dictionary"
        record = Inventory()
        self.assertRaises(DataValidationError, record.deserialize, data)


    def test_deserialize_bad_type_fields(self):
        record = InventoryFactory()
        request = record.serialize()
        for field in ["quantity", "reorder_quantity", "restock_level"]:
            temp = request[field]
            request[field] = "100"
            self.assertRaises(DataValidationError, record.deserialize, request)
            request[field] = temp


    def test_deserialize_out_of_range_values(self):
        record = InventoryFactory()
        request = record.serialize()
        for field in ["quantity", "reorder_quantity", "restock_level"]:
            temp = request[field]
            request[field] = -20
            self.assertRaises(OutOfRangeError, record.deserialize, request)
            request[field] = temp


    def test_read_a_record(self):
        """It should Read a Record"""
        record = InventoryFactory()
        logging.debug(record)
        record.create()
        self.assertIsNotNone(record.product_id)
        # Fetch it back
        found_record = record.find((record.product_id,record.condition))
        self.assertEqual(found_record.product_id, record.product_id)
        self.assertEqual(found_record.condition, record.condition)


    def test_delete_a_record(self):
        """Test to check if record is deleted"""
        inventory_record = InventoryFactory()
        inventory_record.create()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the inventory_record and make sure it isn't in the database
        inventory_record.delete()
        self.assertEqual(len(Inventory.all()), 0)


    def test_update_a_record(self):
        """It should Update a Record"""
        record = InventoryFactory()
        logging.debug(record)
        record.create()
        self.assertIsNotNone(record.product_id)

        request_body = record.serialize()
        request_body["quantity"] = 10
        request_body["restock_level"] = 2
        request_body["reorder_quantity"] = 15
        new_data = Inventory()
        new_data.deserialize(request_body)
        record.update(new_data)

        self.assertEqual(record.serialize(), request_body)
