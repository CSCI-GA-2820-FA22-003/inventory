"""
Inventory
"""
import logging

from flask import jsonify, request, abort
from flask_restx import Resource, fields, reqparse, inputs
from service.models import Inventory
from .common import status  # HTTP Status Codes

# Import Flask application
from . import app, api

app.url_map.strict_slashes = False


@app.route("/health", methods=["GET"])
def health():
    """ Health endpoint """
    app.logger.info("Service active, health endpoint successfully called")
    return jsonify(status="OK"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    app.logger.info("Request for Root URL")
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
create_model = api.model('Inventory', {
    'name': fields.String(
        required=True,
        description='The name of the Inventory'
    ),
    'condition': fields.String(
        required=True,
        description='The condition type',
        enum=Inventory.Condition._member_names_
    ),
    'quantity': fields.Integer(
        required=True,
        description='Quantity of inventory type'
    ),
    'reorder_quantity': fields.Integer(
        description='The reorder quantity of the Inventory'
    ),
    'restock_level': fields.Integer(
        description='The restock_level of the Inventory'
    ),
    'active': fields.Boolean(
        required=True,
        description='Active status inventory'
    )
})

inventory_model = api.inherit(
    'InventoryModel',
    create_model,
    {
        'product_id': fields.Integer(
            readOnly=True,
            description='The unique id assigned internally by service'),
    }
)


# query string arguments
inventory_args = reqparse.RequestParser()
inventory_args.add_argument(
    'status', type=inputs.boolean, required=False, help='List Inventory by status'
)


######################################################################
#  PATH: /inventory/{product_id}/{condition}
######################################################################
@api.route('/inventory/<product_id>/<condition>')
@api.param('product_id', 'The Inventory identifier')
class InventoryResource(Resource):
    """Resource for CRUD operations on Inventory

    Allows the manipulation of a single Inventory
    GET /inventory/<product_id>/<condition> - Returns a Inventory with the id
    PUT /inventory/<product_id>/<condition> - Update a Inventory with the id
    DELETE /inventory/<product_id>/<condition> -  Deletes a Inventory with the id
    POST /inventory/<product_id>/<condition> -  Create a Inventory with the id
    """
    @api.doc('get_inventory')
    @api.response(404, 'Pet not found')
    @api.marshal_with(inventory_model)
    def get(self, product_id, condition):
        """
        Retrieve a single Inventory
        This endpoint will return a Inventory based on it's id and condition
        """
        app.logger.info("Finding the given record inside InventoryResource")
        inventory = Inventory.find((product_id, condition))
        if not inventory:
            abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
        app.logger.info("Returning product: %s", inventory.name)
        return inventory.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING INVENTORY
    # ------------------------------------------------------------------
    @api.doc('update_inventory')
    @api.response(400, 'The posted Inventory data was not valid')
    @api.response(404, 'Inventory not found')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    def put(self, product_id, condition):
        """Update the record of an existing product in the Inventory database"""
        app.logger.info("Update an inventory record inside InventoryResource")
        # Retrieve item from table
        new_record = Inventory()
        new_record.deserialize(request.get_json())
        existing_record = Inventory.find((product_id, condition))

        if not existing_record:
            abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

        # Apply update to database & return as JSON
        existing_record.update(new_record)
        return existing_record.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A INVENTORY
    # ------------------------------------------------------------------
    @api.doc('delete_inventory')
    @api.response(204, 'Inventory deleted')
    def delete(self, product_id, condition):
        """Delete a record on the basis of the specified
        product_id and condition"""
        app.logger.info("Request to delete inventory record with id: "
                        f"{product_id} with condition: {condition}")
        inventory = Inventory.find((product_id, condition))
        app.logger.info("For the provided id, Inventory Record returned is:"
                        f'{inventory}')
        if not inventory:
            return "", status.HTTP_204_NO_CONTENT
        inventory.delete()
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /inventory
######################################################################
@api.route('/inventory')
class InventoryCollection(Resource):
    """ Handles all interactions with collections of inventory """
    # ------------------------------------------------------------------
    # LIST ALL PRODUCTS IN INVENTORY
    # ------------------------------------------------------------------
    @api.doc('list_inventory')
    @api.expect(inventory_args, validate=True)
    @api.marshal_list_with(inventory_model)
    def get(self):
        """returns all the products in the inventory"""
        records = []
        feature_flag = False
        req = {}

        product_id=request.args.get("product_id")
        name = request.args.get("name")
        condition = request.args.get("condition")
        quantity = request.args.get("quantity")
        operator = request.args.get("operator")

        active = request.args.get("active")
        if active is not None:
            if active == 'True':
                active = True
            else:
                active = False
        if product_id:
            app.logger.info("Filtering by name: %s", name)
            feature_flag = True
            req["product_id"] = product_id
        if name:
            app.logger.info("Filtering by name: %s", name)
            feature_flag = True
            req["name"] = name
        if condition:
            app.logger.info("Filtering by condition:%s", condition)
            condition = Inventory.Condition(condition)
            feature_flag = True
            req["condition"] = condition
        if quantity:
            app.logger.info("Filtering by quantity: %s", quantity)
            feature_flag = True
            req["quantity"] = (quantity, operator)
        if active is not None:
            app.logger.info("Filtering by available: %s", active)
            feature_flag = True
            req["active"] = active

        if feature_flag:
            records = Inventory.find_by_general_filter(req)
            if records == "Invalid":
                abort(status.HTTP_400_BAD_REQUEST)
        else:
            app.logger.info("Request list of all inventory records")
            records = Inventory.all()
        results = [record.serialize() for record in records]
        app.logger.info("Returning %d inventory records", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PRODUCT TO THE INVENTORY
    # ------------------------------------------------------------------
    @api.doc('create_inventory')
    @api.response(400, 'The posted data was not valid')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model, code=201)
    def post(self):
        """
        Creates an inventory
        This endpoint will create an inventory based the data in the body that is posted
        """
        app.logger.info("Request to create a record")
        check_content_type("application/json")
        inventory = Inventory()
        data = request.get_json()
        # if not inventory.check_primary_key_valid(data):
        #     abort(status.HTTP_409_CONFLICT, "Primary key missing/invalid")
        inventory.deserialize(data)

        existing_inventory = Inventory.find((inventory.product_id, inventory.condition))
        if existing_inventory:
            error = "Product with id \'" + str(inventory.product_id)
            error += "\'and condition\'" + str(inventory.condition)
            error += "\'already exists."
            abort(status.HTTP_409_CONFLICT, error)

        inventory.create()
        # location_url = url_for("",
        #                     product_id=inventory.product_id,
        #                     condition=inventory.condition, _external=True)
        statement = f"Inventory product with ID {inventory.product_id}" \
                    f"and condition: {inventory.condition} created."
        logging.debug(statement)
        return inventory.serialize(), status.HTTP_201_CREATED
        # return jsonify(inventory.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


@api.route('/inventory/checkout/<product_id>/<condition>')
class InventoryCheckout(Resource):
    # ------------------------------------------------------------------
    # CHECKOUT A FIXED QUANTITY OF A PRODUCT IN THE INVENTORY DB
    # ------------------------------------------------------------------
    @api.doc('checkout_inventory')
    @api.response(400, 'The posted Inventory data was not valid')
    @api.response(404, 'Inventory not found')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    def put(self, product_id, condition):
        """Reduces quantity from inventory of a particular item based on the amount specified by user"""
        data = request.get_json()
        existing_record = Inventory.find((product_id, condition))
        if not existing_record:
            abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
        else:
            existing_record.checkout(data)
            return existing_record.serialize(), status.HTTP_200_OK


@api.route('/inventory/reorder/<product_id>/<condition>')
class InventoryReorder(Resource):
    # ------------------------------------------------------------------
    # REORDER FIXED QUANTITY OF A PRODUCT IN THE INVENTORY DB
    # ------------------------------------------------------------------
    @api.doc('reorder_inventory')
    @api.response(400, 'The posted Inventory data was not valid')
    @api.response(404, 'Inventory not found')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    def put(self, product_id, condition):
        """Increases quantity from inventory of a particular item
        based on the amount specified by user"""
        app.logger.info(f"Reorder called for product id: {product_id}, condition: {condition}")

        data = request.get_json()
        existing_record = Inventory.find((product_id, condition))
        if not existing_record:
            abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
        existing_record.reorder(data)
        return existing_record.serialize(), status.HTTP_200_OK

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


@app.before_first_request
def init_db():
    """ Initializes the SQLAlchemy app """
    Inventory.init_db(app)


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
