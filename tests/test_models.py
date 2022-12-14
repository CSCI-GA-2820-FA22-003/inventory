"""
Test cases for Inventory Model

"""
import logging
import os
import unittest

from service import app
from service.models import DataValidationError, InactiveRecordError, Inventory, OutOfRangeError, db
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
                           quantity=10,)
        self.assertTrue(record is not None)
        self.assertEqual(str(record), "<Inventory %r product_id=[%d] condition=[%s]>" %
                         ("monitor", 1, Inventory.Condition.NEW.name))
        self.assertEqual(record.product_id, 1)
        self.assertEqual(record.name, "monitor")
        self.assertEqual(record.condition, Inventory.Condition.NEW)
        self.assertEqual(record.quantity, 10)
        # self.assertEqual(record.reorder_quantity, 20)
        # self.assertEqual(record.restock_level, 2)

    def test_inventory_serialize(self):
        record = Inventory(product_id=1, name="monitor", condition=Inventory.Condition.NEW,
                           quantity=10, active=True)
        actual_output = record.serialize()
        expected_output = {
            "product_id": 1,
            "name": "monitor",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            # "reorder_quantity": 20,
            # "restock_level": 2,
            "active": True
        }
        self.assertEqual(actual_output, expected_output)

    def test_inventory_deserialize(self):
        data = {
            "product_id": 1,
            "name": "monitor",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            # "reorder_quantity": 20,
            # "restock_level": 2
        }
        record = Inventory()
        record.deserialize(data)
        self.assertEqual(record.product_id, 1)
        self.assertEqual(record.name, "monitor")
        self.assertEqual(record.condition, Inventory.Condition.NEW)
        self.assertEqual(record.quantity, 10)
        # self.assertEqual(record.reorder_quantity, 20)
        # self.assertEqual(record.restock_level, 2)

    def test_inventory_deserialize_missing_keys(self):
        """Test check_primary_key_valid false"""
        data = {
            "name": "monitor",
            "wrong_quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
        }
        record = Inventory()
        record.deserialize(data)
        self.assertEqual(record.product_id, None)

    def test_inventory_deserialize_wrong_value_types(self):
        """Test check_primary_key_valid false"""
        data = {
            "product_id": "WRONG_TYPE",
            "name": "monitor",
            "condition": 1,
            "wrong_quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
        }
        record = Inventory()
        record.deserialize(data)
        self.assertEqual(record.product_id, None)

    def test_deserialize_wrong_type_name(self):
        """It should not deserialize inventory with wrong type of name"""
        data = {
            "product_id": 1,
            "name": 2,
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
        }
        record = Inventory()
        self.assertRaises(DataValidationError, record.deserialize, data)

    def test_deserialize_wrong_type_active(self):
        """It should not deserialize inventory with wrong type of active"""
        data = {
            "active": "wrong_type",
            "product_id": 1,
            "name": "laptop",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
        }
        record = Inventory()
        self.assertRaises(DataValidationError, record.deserialize, data)

    def test_inventory_deserialize_partial_fields(self):
        """Test Inventory deserializer for partially available fields"""
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
        # self.assertEqual(record.reorder_quantity, None)
        # self.assertEqual(record.restock_level, None)

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
        """Test to check deserialization of invalid values"""
        record = InventoryFactory()
        request = record.serialize()
        for field in ["quantity"]:
            temp = request[field]
            request[field] = "100"
            self.assertRaises(DataValidationError, record.deserialize, request)
            request[field] = temp

    def test_deserialize_out_of_range_values(self):
        """Test to deserialize out of range values"""
        record = InventoryFactory()
        request = record.serialize()
        for field in ["quantity"]:
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
        found_record = record.find((record.product_id, record.condition))
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
        record.create()
        self.assertIsNotNone(record.product_id)

        request_body = record.serialize()
        request_body["quantity"] = 10
        # request_body["restock_level"] = 2
        # request_body["reorder_quantity"] = 15
        new_data = Inventory()
        new_data.deserialize(request_body)
        record.update(new_data)

        self.assertEqual(record.serialize(), request_body)

    def test_checkout_success(self):
        """Test for checkout success"""
        record = InventoryFactory()
        record.create()
        record.active = True
        self.assertIsNotNone(record.product_id)

        original_quantity = record.quantity
        data = {}
        data["ordered_quantity"] = 1
        record.checkout(data)
        self.assertEqual(record.quantity, original_quantity-1)

    def test_checkout_inactive_exception(self):
        """Test for checkout at inactive status"""
        record = InventoryFactory()
        record.create()
        record.active = False
        self.assertIsNotNone(record.product_id)
        data = {}
        data["ordered_quantity"] = 1
        self.assertRaises(InactiveRecordError, record.checkout, data)

    def test_checkout_quantity_type_exception(self):
        """Test for checkout at wrong quantity type"""
        record = InventoryFactory()
        record.create()
        record.active = True
        self.assertIsNotNone(record.product_id)

        data = {}
        data["ordered_quantity"] = "1"
        self.assertRaises(DataValidationError, record.checkout, data)

    def test_checkout_exceed_exception(self):
        """Test for checkout exceed exception"""
        record = InventoryFactory()
        record.create()
        record.active = True
        self.assertIsNotNone(record.product_id)

        original_quantity = record.quantity
        data = {}
        data["ordered_quantity"] = original_quantity + 1
        self.assertRaises(OutOfRangeError, record.checkout, data)

    def test_reorder(self):
        """Test for reorder success"""
        record = InventoryFactory()
        record.create()
        record.active = True
        self.assertIsNotNone(record.product_id)

        # reorder succeeds
        original_quantity = record.quantity
        data = {"ordered_quantity": 1}
        record.reorder(data)
        self.assertEqual(record.quantity - original_quantity, 1)

        # reorder fails with invalid data type
        self.assertRaises(DataValidationError, record.reorder, {})
        self.assertRaises(DataValidationError, record.reorder, {"ordered_quantity": "1"})

        # reorder fails when record is inactive
        record.active = False
        self.assertRaises(InactiveRecordError, record.reorder, data)
