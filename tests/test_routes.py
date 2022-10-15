"""
TestInventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app, routes
from service.models import Inventory, db, init_db
from service.common import status  # HTTP Status Codes
from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/inventory-records"
######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventory(TestCase):
    """ Test Cases for Inventory Routes """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        #set up the connection with the database
        init_db(app)
        

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()


    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_records(self):
        """ Test Create Records """
        test_record = InventoryFactory()
        logging.debug("Test Inventory Record: %s", test_record.serialize())
        #raise Exception(test_record.serialize())
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # # Make sure location header is set
        # location = response.headers.get("Location", None)
        # self.assertIsNotNone(location)

        # # Check the data is correct
        # new_record = response.get_json()
        # self.assertEqual(new_record["name"], test_record.name)
        # self.assertEqual(new_record["condition"], test_record.condition.name)
        # self.assertEqual(new_record["quantity"], test_record.quantity)
        # self.assertEqual(new_record["reorder_quantity"], test_record.reorder_quantity)
        # self.assertEqual(new_record["restock_level"], test_record.restock_level)


        # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_record = response.get_json()
        # self.assertEqual(new_record["name"], test_record.name)
        # self.assertEqual(new_record["condition"], test_record.condition.name)
        # self.assertEqual(new_record["quantity"], test_record.quantity)
        # self.assertEqual(new_record["reorder_quantity"], test_record.reorder_quantity)
        # self.assertEqual(new_record["restock_level"], test_record.restock_level)
