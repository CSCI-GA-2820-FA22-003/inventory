"""
TestInventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import logging
import os
import random
from urllib.parse import quote_plus
from unittest import TestCase

from service import app
from service.common import status  # HTTP Status Codes
from service.models import Inventory, db, init_db
from tests.factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/inventory"
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
        # set up the connection with the database
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


    def _create_inventory_records(self, count):
        """Factory method to create inventory records in bulk"""
        records = []
        for _ in range(count):
            test_record = InventoryFactory()
            response = self.client.post(BASE_URL, json=test_record.serialize())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            records.append(test_record)
        return records

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_inventory_records(self):
        """ Test Create Products """
        test_record = InventoryFactory()
        logging.debug("Test Inventory Records: %s", test_record.serialize())
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_record = response.get_json()
        self.assertEqual(new_record["product_id"], test_record.product_id)
        self.assertEqual(new_record["name"], test_record.name)
        self.assertEqual(new_record["condition"], test_record.condition.value)
        self.assertEqual(new_record["quantity"], test_record.quantity)
        self.assertEqual(new_record["reorder_quantity"], test_record.reorder_quantity)
        self.assertEqual(new_record["restock_level"], test_record.restock_level)
        self.assertEqual(new_record["active"], test_record.active)

    def test_create_inventory_records_with_defaults(self):
        """ Test Create Products With Defaults success"""
        test_record = InventoryFactory()
        request_body = {
            "product_id": test_record.product_id,
            "name": test_record.name,
            "condition": test_record.condition.value
        }

        logging.debug("Test Inventory Records: %s", request_body)
        response = self.client.post(BASE_URL, json=request_body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_record = response.get_json()
        self.assertEqual(new_record["product_id"], test_record.product_id)
        self.assertEqual(new_record["name"], test_record.name)
        self.assertEqual(new_record["condition"], test_record.condition.value)
        self.assertEqual(new_record["quantity"], 0)
        self.assertEqual(new_record["reorder_quantity"], 0)
        self.assertEqual(new_record["restock_level"], 0)
        self.assertEqual(new_record["active"], True)

        # uncomment this once list all products works
        # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_record = response.get_json()
        # self.assertEqual(new_record["id"], test_record.id)
        # self.assertEqual(new_record["name"], test_record.name)
        # self.assertEqual(new_record["condition"], test_record.condition.value)
        # self.assertEqual(new_record["quantity"], test_record.quantity)
        # self.assertEqual(new_record["reorder_quantity"], test_record.reorder_quantity)
        # self.assertEqual(new_record["restock_level"], test_record.restock_level)


    def test_create_alreadyexists_record(self):
        """Test if a record already exists"""
        
        test_record = InventoryFactory()
        logging.debug("New Inventory Record: %s", test_record.serialize())
        
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

       # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_record = response.get_json()
        self.assertEqual(new_record["product_id"], test_record.product_id)
        self.assertEqual(new_record["name"], test_record.name)
        self.assertEqual(new_record["condition"], test_record.condition.value)
        self.assertEqual(new_record["quantity"], test_record.quantity)
        self.assertEqual(new_record["reorder_quantity"], test_record.reorder_quantity)
        self.assertEqual(new_record["restock_level"], test_record.restock_level)
        self.assertEqual(new_record["active"], test_record.active)

        # Create a new record with the same data values as just inserted into the database, this should return a 409 conflict
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


    def test_create_record_invalid_content_type(self):
        """Test if the user input is of invalid content type"""
        
        input_data = {
            "id": 1,
            "name": "monitor",
            "condition": Inventory.Condition.NEW.value,
            "quantity": 10,
            "reorder_quantity": 20,
            "restock_level": 2
            }
        
        logging.debug("New Inventory Record: %s", input_data)
        
        # this will test when a json is passed by cannot be parsed
        response = self.client.post(BASE_URL, data=input_data)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        # this will test when a string is passed which has invalid request headers
        response = self.client.post(BASE_URL, data="1")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


    def test_delete_inventory_record_success(self):
        """Test to check if it deletes an inventory record"""
        test_record = self._create_inventory_records(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_record.product_id}/{test_record.condition.name}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_record.product_id}/{test_record.condition.name}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_inventory_record_exception(self):
        """Test to check if code deletes non-existent record"""
        SAMPLE_PRODUCT_ID = 10
        SAMPLE_CONDITION = 'NEW'
        response = self.client.delete(f"{BASE_URL}/{SAMPLE_PRODUCT_ID}/{SAMPLE_CONDITION}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_list_inventory_records(self):
        """Test to successfully list all inventory records"""
        expected_records = self._create_inventory_records(2)
        expected_response = [record.serialize() for record in expected_records]
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertCountEqual(expected_response, data)


    def test_update_non_existent_inventory_records(self):
        """Test to update non-existent inventory records"""
        test_record = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        logging.debug('Created record, %s', Inventory().deserialize(response.get_json()))
        data = response.get_json()
        # increment product_id so that query searches for a different product_id
        data['product_id'] += 1
        response = self.client.put(f"{BASE_URL}/{data['product_id']}/{test_record.condition.name}"
                                   , json=data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_update_inventory_records(self):
        """Test for successful update of an inventory record with valid values"""
        # Create a test record
        test_record = self._create_inventory_records(1)[0]
        data = test_record.serialize()
        data["quantity"] += 1
        data["reorder_quantity"] += 1
        data["restock_level"] += 1
        data["name"] = "some_name"
        # Make call to update record
        response = self.client.put(f"{BASE_URL}/{data['product_id']}/{test_record.condition.name}", json=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_record = response.get_json()
        self.assertEqual(data, updated_record)


    def test_attempt_incorrect_value_update(self):
        """Test to check if a record gets updated with an invalid value for a particular field"""
        test_record = self._create_inventory_records(1)[0]
        data = test_record.serialize()

        for field in ["quantity", "reorder_quantity", "restock_level"]:
            temp = data[field]
            data[field] = '100'
            response = self.client.put(f"{BASE_URL}/{data['product_id']}/{data['condition']}",
                                       json=data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            data[field] = temp

        for field in ["quantity", "reorder_quantity", "restock_level"]:
            temp = data[field]
            data[field] = -20
            response = self.client.put(f"{BASE_URL}/{data['product_id']}/{data['condition']}",
                                       json=data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            data[field] = temp


    def update_non_existent_record(self):
        """Update a record that does not exist in the database"""
        test_record = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        logging.debug('Created record, %s', Inventory().deserialize(response.get_json()))

        # Get record as JSON
        data = response.get_json()
        data['product_id'] += 100
        response = self.client.put(f"{BASE_URL}/{data['product_id']}/{data['condition']}",
                                   json=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_read_records(self):
        """Test to read a record successfully existing from within database"""
        record = self._create_inventory_records(1)[0]
        record.name = None
        record.quantity  = None
        record.reorder_quantity = None
        record.restock_level = None
        logging.debug("Test Read Records: %s", record.serialize())
        response = self.client.get(f"{BASE_URL}/{record.product_id}/{record.condition.name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["product_id"], record.product_id)
        self.assertEqual(data["condition"], record.condition.value)


    def test_read_non_existent_records(self):
        """Test to attempt reading records that do not exist in the database"""
        record = self._create_inventory_records(1)[0]
        record.product_id = record.product_id + 1
        record.name = None
        record.quantity  = None
        record.reorder_quantity = None
        record.restock_level = None
        logging.debug("Test Read Records: %s", record.serialize())
        response = self.client.get(f"{BASE_URL}/{record.product_id}", json= record.serialize())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_method_not_allowed(self):
        """Test if API is called with the wrong method type"""
        test_record = InventoryFactory()
         
        # calling a delete method without product id
        logging.debug("Test Inventory Records with method not allowed delete request: %s", test_record.serialize())
        response = self.client.delete(f"{BASE_URL}", json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # calling an update method without product id
        logging.debug("Test Inventory Records with method not allowed update request: %s", test_record.serialize())
        response = self.client.put(f"{BASE_URL}", json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

######################################################################
    # T E S T   Q U E R Y   S T R I N G S
######################################################################

    def test_query_inventories_by_name(self):
        """It should Query Inventories by Name Individually"""
        records = self._create_inventory_records(10)
        test_name = records[0].name
        name_list = [record for record in records if record.name == test_name]
        logging.info("Name=%s: %d = %s", test_name, len(name_list), name_list)
        resp = self.client.get(BASE_URL, query_string=f"name={quote_plus(test_name)}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(name_list))
        # check the data just to be sure
        for record in data:
            self.assertEqual(record["name"], test_name)

    def test_query_inventories_by_condition(self):
        """It should Query Inventories by Condition Individually"""
        records = self._create_inventory_records(1)
        test_condition = records[0].condition
        condition_list = [record for record in records if record.condition.name == test_condition.name]
        logging.info(
            "Category=%s: %d = %s", test_condition, len(condition_list), condition_list
        )
        resp = self.client.get(
            BASE_URL, query_string=f"condition={quote_plus(test_condition.value)}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(condition_list))
        # check the data just to be sure
        for record in data:
            self.assertEqual(record["condition"], test_condition.value)

    def test_query_inventories_by_active(self):
        """It should Query Inventories by Availability Individually"""
        records = self._create_inventory_records(10)
        test_active = records[0].active
        active_list = [record for record in records if record.active == test_active]
        logging.info(
            "Active=%s: %d = %s", test_active, len(active_list), active_list
        )
        resp = self.client.get(BASE_URL, query_string=f"active={test_active}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(active_list))
        # check the data just to be sure
        for record in data:
            self.assertEqual(record["active"], test_active)

    def test_query_inventories_by_equal_quantity(self):
        """It should Query Inventories by Equal Quantity Individually"""
        records = self._create_inventory_records(10)
        test_quantity = records[0].quantity
        quantity_list = [record for record in records if record.quantity == test_quantity]
        test_operator="="
        logging.info(
            "Quantity=%s: %d = %s", test_quantity, len(quantity_list), quantity_list
        )
        resp = self.client.get(BASE_URL, query_string=f"quantity={str(test_quantity)}&operator={test_operator}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(quantity_list))
        # check the data just to be sure
        for record in data:
            self.assertEqual(record["quantity"], test_quantity)

    def test_query_inventories_by_invalid_operator_quantity(self):
        """It should Query Inventories by Invalid operator Quantity Individually"""
        records = self._create_inventory_records(10)
        test_quantity = records[0].quantity
        quantity_list = [record for record in records if record.quantity == test_quantity]
        test_operator="=="
        logging.info(
            "Quantity=%s: %d = %s", test_quantity, len(quantity_list), quantity_list
        )
        resp = self.client.get(BASE_URL, query_string=f"quantity={str(test_quantity)}&operator={test_operator}")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_inventories_by_less_than_quantity(self):
        """It should Query Inventories by Less Than Quantity Individually"""
        records = self._create_inventory_records(10)
        test_quantity = records[0].quantity
        quantity_list = [record for record in records if record.quantity < test_quantity]
        test_operator="<"
        logging.info(
            "Quantity=%s: %d = %s", test_quantity, len(quantity_list), quantity_list
        )
        resp = self.client.get(BASE_URL, query_string=f"quantity={str(test_quantity)}&operator={test_operator}")
        if len(quantity_list) > 0:
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            data = resp.get_json()
            self.assertEqual(len(data), len(quantity_list))
            # check the data just to be sure
            for record in data:
                self.assertLess(record["quantity"], test_quantity)
        else:
            self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_query_inventories_by_less_than_equal_quantity(self):
        """It should Query Inventories by Less Than Equal to Quantity Individually"""
        records = self._create_inventory_records(10)
        test_quantity = records[0].quantity
        quantity_list = [record for record in records if record.quantity <= test_quantity]
        test_operator="<="
        logging.info(
            "Quantity=%s: %d = %s", test_quantity, len(quantity_list), quantity_list
        )
        resp = self.client.get(BASE_URL, query_string=f"quantity={str(test_quantity)}&operator={test_operator}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(quantity_list))
        # check the data just to be sure
        for record in data:
            self.assertLessEqual(record["quantity"], test_quantity)
    
    def test_query_inventories_by_greater_than_equal_quantity(self):
        """It should Query Inventories by Greater Than Equal to Quantity Individually"""
        records = self._create_inventory_records(10)
        test_quantity = records[0].quantity
        quantity_list = [record for record in records if record.quantity >= test_quantity]
        test_operator=">="
        logging.info(
            "Quantity=%s: %d = %s", test_quantity, len(quantity_list), quantity_list
        )
        resp = self.client.get(BASE_URL, query_string=f"quantity={str(test_quantity)}&operator={test_operator}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(quantity_list))
        # check the data just to be sure
        for record in data:
            self.assertGreaterEqual(record["quantity"], test_quantity)

    def test_query_inventories_by_greater_than_quantity(self):
        """It should Query Inventories by Greater Than Quantity Individually"""
        records = self._create_inventory_records(10)
        test_quantity = records[0].quantity
        quantity_list = [record for record in records if record.quantity > test_quantity]
        test_operator=">"
        logging.info(
            "Quantity=%s: %d = %s", test_quantity, len(quantity_list), quantity_list
        )
        resp = self.client.get(BASE_URL, query_string=f"quantity={str(test_quantity)}&operator={test_operator}")
        if(len(quantity_list)>0):
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            data = resp.get_json()
            self.assertEqual(len(data), len(quantity_list))
            # check the data just to be sure
            for record in data:
                self.assertGreater(record["quantity"], test_quantity)
        else:
            self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_query_inventories_by_combinations(self):
        """It should Query Inventories by combined filters"""
        records = self._create_inventory_records(10)
        ######## Filtering by name and conditions
        test_name = records[0].name
        test_condition=records[0].condition
        lists = [record for record in records if record.name == test_name and record.condition.name==test_condition.name]
        logging.info("Name=%s and Condition=%s: %d = %s", test_name, test_condition,len(lists), lists)
        resp = self.client.get(BASE_URL, query_string=f"name={quote_plus(test_name)}&condition={quote_plus(test_condition.value)}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(lists))
        # check the data just to be sure
        for record in data:
            self.assertEqual(record["name"], test_name)
            self.assertEqual(record["condition"], test_condition.value)
        ######## Filtering by condition and available status
        test_condition = records[0].condition
        test_active=records[0].active
        lists = [record for record in records if record.condition.name == test_condition.name and record.active==test_active]
        logging.info("Condition=%s and Active=%s: %d = %s", test_condition, test_active,len(lists), lists)
        resp = self.client.get(BASE_URL, query_string=f"condition={quote_plus(test_condition.value)}&active={quote_plus(str(test_active))}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(lists))
        # check the data just to be sure
        for record in data:
            self.assertEqual(record["condition"], test_condition.value)
            self.assertEqual(record["active"], test_active)

######################################################################
    # T E S T   H E A L T H 
###################################################################### 
    def test_health(self):
        """ It should call the health endpoint """
        response = self.client.get("/health")
        self.assertEqual(response.get_json(), {"status": "OK"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_checkout_features_failure_invalid_product_id(self):
        """Test for cases when the checkout feature fails if product is not in the database"""
        test_record = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        logging.debug('Created record, %s', Inventory().deserialize(response.get_json()))

        # Get record as JSON
        data = response.get_json()
        request_dict = dict()
        request_dict['ordered_quantity'] = data['quantity'] + 1
        response = self.client.put(f"{BASE_URL}/checkout/{data['product_id'] + 1}"
                                   f"/{test_record.condition.name}",
                                   json=request_dict)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    

    def test_reorder(self):
        """"Test for cases when reorder endpoint is called"""
        record = InventoryFactory()
        record.active = True
        response = self.client.post(BASE_URL, json=record.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        request_body = {"ordered_quantity": 1}
        expected_data = record.serialize()
        expected_data["quantity"] += request_body["ordered_quantity"]

        # success: 200
        url = f"{BASE_URL}/reorder/{record.product_id}/{record.condition.name}"
        response = self.client.put(url, json=request_body)
        actual_data = response.get_json()

        self.assertEqual(actual_data, expected_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # product not found: 404
        url = f"{BASE_URL}/reorder/{record.product_id+1}/{record.condition.name}"
        response = self.client.put(url, json=request_body)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    # def test_checkout_success(self):
    #     """Test for cases when the checkout feature executes successfully
    #     when ordered quantity is less than quantity of item in the database"""
    #     test_record = InventoryFactory()
    #     response = self.client.post(BASE_URL, json=test_record.serialize())
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     logging.debug('Created record, %s', Inventory().deserialize(response.get_json()))

    #     # Get record as JSON
    #     data = response.get_json()
    #     request_dict = dict()
    #     request_dict['ordered_quantity'] = data['quantity'] - 1
    #     response = self.client.put(f"{BASE_URL}/checkout/{data['product_id']}"
    #                                f"/{data['condition']}",
    #                                json=request_dict)
    #     response_dict = response.get_json()
    #     self.assertEqual(response_dict['quantity'], 1)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
