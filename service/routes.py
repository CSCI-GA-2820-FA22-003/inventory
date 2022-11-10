"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
from .common import status  # HTTP Status Codes
from service.models import Inventory


# Import Flask application
from . import app


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
    global app
    Inventory.init_db(app)


@app.route("/inventory/<product_id>", methods=["GET"])
def get_inventory_records(product_id):
    """
    Retrieve a single record
    This endpoint will return a record based on it's product id and condition
    """
    # fetch the condition from the payload of the data
    app.logger.info("Reading the given record")
    check_content_type("application/json")

    inventory = find_from_request_json(request.get_json())

    if not inventory:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    app.logger.info("Returning product: %s", inventory.name)
    return jsonify(inventory.serialize()), status.HTTP_200_OK


@app.route("/inventory", methods=["POST"])
def create_inventory_records():
    """
    Creates inventory record
    This end point will create an inventory record and store it in the database based on user input in the body
    """
    app.logger.info("Request to create a record")
    check_content_type("application/json")
    inventory = Inventory()
    data = request.get_json()
    inventory.deserialize(data)
    existing_inventory = Inventory.find((inventory.product_id, inventory.condition))
    if existing_inventory:
        error = f"Product with id '{inventory.product_id}' and condition '{inventory.condition}' already exists."
        abort(status.HTTP_409_CONFLICT, error)

    inventory.create()
    location_url = url_for("get_inventory_records", product_id=inventory.product_id, _external=True)

    app.logger.info(f"Inventory product with ID {inventory.product_id} and condition: {inventory.condition} created.")
    # return jsonify(inventory.serialize()), status.HTTP_201_CREATED
    return jsonify(inventory.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


@app.route("/inventory", methods=["GET"])
def list_inventory_records():
    """Returns all of the Inventory records"""
    records=[]
    name = request.args.get("name")
    condition = request.args.get("condition")
    quantity = request.args.get("quantity")
    active = request.args.get("active")

    if name:
        app.logger.info("Filtering by name: %s", name)
        records = Inventory.find_by_name(name)
    elif condition:
        app.logger.info("Filtering by condition:%s", condition)
        records = Inventory.find_by_condition(name)
    elif quantity:
        app.logger.info("Filtering by quantity: %s", quantity)
        records = Inventory.find_by_quantity(quantity)
    elif active:
        app.logger.info("Filtering by available: %s", active)
        is_active = active.lower() in ["yes", "y", "true", "t", "1"]
        records = Inventory.find_by_active(is_active)
    else:
        app.logger.info("Request list of all inventory records")
        records = Inventory.all()

    
    
    results = [record.serialize() for record in records]
    app.logger.info("Returning %d inventory records", len(results))
    return jsonify(results), status.HTTP_200_OK


@app.route("/inventory/<product_id>", methods=["DELETE"])
def delete_inventory_record(product_id):
    """Deletes inventory record

    @param: product_id is the id of the record that is to be deleted
    """
    app.logger.info("Request to delete inventory record with id: %s", product_id)
    inventory = find_from_request_json(request.get_json())
    app.logger.info(f"For the provided id, Inventory Record returned is: {inventory}")

    if inventory:
        inventory.delete()
    else:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    app.logger.info(f"Inventory record with ID {product_id} delete complete.")
    return "", status.HTTP_204_NO_CONTENT


@app.route("/inventory/<int:product_id>/", methods=["PUT"])
@app.route("/inventory/<int:product_id>", methods=["PUT"])
def update_inventory_records(product_id):
    """Updates an existing inventory record given that it is present in the database table"""
    app.logger.info("Update an inventory record")
    # Retrieve item from table
    new_record = Inventory()
    new_record.deserialize(request.get_json())
    existing_record = Inventory.find((new_record.product_id, new_record.condition))

    if not existing_record:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    # Apply update to database & return as JSON
    existing_record.update(new_record)
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
    inventory = Inventory()
    inventory.deserialize(request_body)
    return Inventory.find((inventory.product_id, inventory.condition))
