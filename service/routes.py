"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from .common import status  # HTTP Status Codes
from service.models import Inventory
from datetime import datetime


# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Inventory.init_db(app)

# @app.route("/records/<id>/<name>/<condition>/<quantity>/<reorder_quantity>/<restock_level>", methods=["POST"])
# def create(id=None,name=None,condition=Inventory.Condition.NEW,quantity=0, reorder_quantity=0, restock_level=0):
#     app.logger.info(f"Request to create inventory id: {id} named: {name}")
#     inventory = Inventory.find(id)
#     if inventory:
#         abort(status.HTTP_409_CONFLICT, f"Inventory record with id: {id} named: {name} already exists")
    
#     inventory=Inventory(id,name,condition,quantity,reorder_quantity,restock_level,True,datetime.utcnow,datetime.utcnow)
#     inventory.create()

#     return inventory.serialize(),status.HTTP_201_CREATED

@app.route("/inventory-records", methods=["POST"])
def create_records():
    """
    Creates inventory record
    This end point will create an inventory record and store it in the database based on user input in the body
    """
    app.logger.info("Request to create a record")
    check_content_type("application/json")
    inventory = Inventory()
    
    #raise Exception(inventory.deserialize(request.get_json()))
    app.logger.debug("Test Request in routes: %s", inventory.deserialize(request.get_json()))
    inventory.deserialize(request.get_json())
    
    inventory.create()
    # location_url = url_for("get_records", inventory_id=inventory.id, _external=True)

    # app.logger.info(f"Inventory record with ID {inventory.id} and name: {inventory.name} created.")
    # return jsonify(inventory.serialize()), status.HTTP_201_CREATED, {"Location": location_url}
    return {},status.HTTP_201_CREATED
   
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


    

    