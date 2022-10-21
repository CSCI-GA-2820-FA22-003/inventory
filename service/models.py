"""
Models for Inventory

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum
from flask import Flask


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Inventory.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class OutOfRangeError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class Inventory(db.Model):
    """
    Class that represents a Inventory
    """

    class Condition(enum.Enum):
        NEW = 'new'
        REFURBISHED = 'refurbished'
        RETURN = 'return'

    app = None

    # Table Schema
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(63), nullable=False)
    condition = db.Column(db.Enum(Condition), nullable=False, default=Condition.NEW.name, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_quantity = db.Column(db.Integer, nullable=False, default=0)
    restock_level = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return "<Inventory %r product_id=[%s] condition=[%s]>" % (self.name, self.product_id, self.condition.value)

    def create(self):
        """
        Creates a Inventory to the database
        """
        logger.info("Creating %s", self.name)
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Inventory to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Inventory from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Inventory into a dictionary """
        return {
            "product_id": self.product_id,
            "name": self.name,
            "condition": self.condition.value,
            "quantity": self.quantity,
            "reorder_quantity": self.reorder_quantity,
            "restock_level": self.restock_level
        }

    def deserialize(self, data):
        """
        Deserializes a Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.condition = self.Condition(data["condition"])

            if data.get("name"):
                if isinstance(data.get("name"), str):
                    self.name = data.get("name")
                else:
                    raise TypeError

            for field in ["quantity", "reorder_quantity", "restock_level"]:
                if data.get(field):
                    if not isinstance(data.get(field), int):
                        raise TypeError
                    elif data.get(field) < 0:
                        raise ValueError
                    else:
                        setattr(self, field, data.get(field))

        except KeyError as error:
            raise DataValidationError(
                f"Invalid Inventory: missing {error.args[0]}"
            ) from error
        except TypeError as error:
            raise DataValidationError(
                f"Invalid Inventory: body of request contained bad or no data - Error message: {error}"
            ) from error
        except ValueError as error:
            raise OutOfRangeError(
                f"Invalid Inventory: body of request contained values out of range - Error message: {error}"
            ) from error
        return self

    @classmethod
    def init_db(cls, app: Flask):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Inventories in the database """
        logger.info("Processing all Inventories")
        return cls.query.all()

    @classmethod
    def find(cls, by):
        """ Finds a Inventory by it's ID """
        by_id, by_condition = by
        logger.info("Processing lookup for id %s and condition %s ...", by_id, by_condition)
        return cls.query.get((by_id, by_condition))

    # uncomment for sprint 2
    # @classmethod
    # def find_by_name(cls, name):
    #     """Returns all Inventories with the given name

    #     Args:
    #         name (string): the name of the Inventories you want to match
    #     """
    #     logger.info("Processing name query for %s ...", name)
    #     return cls.query.filter(cls.name == name)
