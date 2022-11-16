"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
from service.models import Inventory
from .common import status  # HTTP Status Codes

# Import Flask application
from . import app

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
    return (
        jsonify(
            name="Inventory Demo REST API Service",
            version="1.0",
            paths=url_for("list_inventory_records", _external=True),
        ),
        status.HTTP_200_OK
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    Inventory.init_db(app)


@app.route("/inventory/<int:product_id>/<condition>", methods=["GET"])
def get_inventory_records(product_id,condition):
    """
    Retrieve a single record
    This endpoint will return a record based on it's product id and condition
    """
    # fetch the condition from the payload of the data
    app.logger.info("Reading the given record")
    
    inventory = Inventory.find((product_id, condition))

    if not inventory:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    app.logger.info("Returning product: %s", inventory.name)
    return jsonify(inventory.serialize()), status.HTTP_200_OK


@app.route("/inventory", methods=["POST"])
def create_inventory_records():
    """
    Creates inventory record
    This end point will create an inventory record and
    store it in the database based on user input in the body
    """
    app.logger.info("Request to create a record")
    check_content_type("application/json")
    inventory = Inventory()
    data = request.get_json()

    # TODO: check if status code is correctly passed below
    if inventory.check_primary_key_valid(data) == False:
        abort(status.HTTP_409_CONFLICT, "Primary key missing/invalid")
    inventory.deserialize(data)

    existing_inventory = Inventory.find((inventory.product_id, inventory.condition))
    if existing_inventory:
        error = "Product with id \'" + str(inventory.product_id)
        error += "\'and condition\'" + str(inventory.condition)
        error += "\'already exists."
        abort(status.HTTP_409_CONFLICT, error)

    inventory.create()
    location_url = url_for("get_inventory_records", product_id=inventory.product_id, condition=inventory.condition, _external=True)
    statement = f"Inventory product with ID {inventory.product_id}" \
    f"and condition: {inventory.condition} created."
    app.logger.info(statement)
    # return jsonify(inventory.serialize()), status.HTTP_201_CREATED

    return jsonify(inventory.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


@app.route("/inventory", methods=["GET"])
def list_inventory_records():
    """Returns all of the Inventory records"""
    records = []
    feature_flag = False
    req = {}

    name = request.args.get("name")
    condition = request.args.get("condition")
    quantity = request.args.get("quantity")
    operator = request.args.get("operator")
    active = request.args.get("active")

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
    if active:
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
    return jsonify(results), status.HTTP_200_OK


@app.route("/inventory/<product_id>/<condition>", methods=["DELETE"])
def delete_inventory_record(product_id, condition):
    """Deletes inventory record

    @param: product_id is the id of the record that is to be deleted
    """
    app.logger.info(f"Request to delete inventory record with id: {product_id} with condition: {condition}")
    inventory = Inventory.find((product_id, condition))
    app.logger.info(f"For the provided id, Inventory Record returned is: {inventory}")
    if not inventory:
        return "", status.HTTP_204_NO_CONTENT
    inventory.delete()
    return "", status.HTTP_204_NO_CONTENT


@app.route("/inventory/<int:product_id>/<condition>", methods=["PUT"])
def update_inventory_records(product_id, condition):
    """Updates an existing inventory record given that it is present in the database table"""
    app.logger.info("Update an inventory record")
    # Retrieve item from table
    new_record = Inventory()
    new_record.deserialize(request.get_json())
    existing_record = Inventory.find((product_id, condition))

    if not existing_record:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    # Apply update to database & return as JSON
    existing_record.update(new_record)
    return jsonify(existing_record.serialize()), status.HTTP_200_OK


@app.route("/inventory/checkout/<int:product_id>/<condition>", methods=["PUT"])
def checkout_quantity(product_id, condition):
    """Reduces quantity from inventory of a particular item based on the amount specified by user"""
    data = request.get_json()
    existing_record = Inventory.find((product_id, condition))
    if not existing_record:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    existing_record.checkout(data)
    return jsonify(existing_record.serialize()), status.HTTP_200_OK

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


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

def find_from_request_json(request_body):
    '''Fetch relevant items based on product ID and condition'''
    inventory = Inventory()
    inventory.deserialize(request_body)
    return Inventory.find((inventory.product_id, inventory.condition))
