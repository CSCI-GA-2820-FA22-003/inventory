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

@app.route("/inventory/<id>/<name>/<condition>/<quantity>/<reorder_quantity>/<restock_level>", methods=["POST"])
def create(id=None,name=None,condition=Inventory.Condition.NEW,quantity=0, reorder_quantity=0, restock_level=0):
    app.logger.info(f"Request to create inventory id: {id} named: {name}")
    inventory = Inventory.find(id)
    if inventory:
        abort(status.HTTP_409_CONFLICT, f"Inventory record with id: {id} named: {name} already exists")
    
    inventory=Inventory(id,name,condition,quantity,reorder_quantity,restock_level,True,datetime.utcnow,datetime.utcnow)
    inventory.create()

    return inventory.serialize(),status.HTTP_201_CREATED
   
    
   


    

    