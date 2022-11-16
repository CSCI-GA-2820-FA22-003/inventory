"""
Models for Inventory

All of the models are stored in this module
"""
import logging
from datetime import datetime
import enum
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Inventory.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

class InactiveRecordError(Exception):
    """ Used when record is inactive"""

class OutOfRangeError(Exception):
    """ Used for an data validation errors when deserializing """


class Inventory(db.Model):
    """
    Class that represents a Inventory
    """

    class Condition(enum.Enum):
        '''Definition of condition values'''
        NEW = 'new'
        REFURBISHED = 'refurbished'
        RETURN = 'return'

    app = None

    # Table Schema
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(63), nullable=False)
    condition = db.Column(db.Enum(Condition), nullable=False,
                          default=Condition.NEW.name, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_quantity = db.Column(db.Integer, nullable=False, default=0)
    restock_level = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def __repr__(self):
        stmt = f"<Inventory '{self.name}' product_id=[{self.product_id}] "
        stmt += f"condition=[{self.condition.name}]>"
        return stmt

    def create(self):
        """
        Creates a Inventory to the database
        """
        logger.info("Creating %s", self.name)
        db.session.add(self)
        db.session.commit()

    def update(self, new_data):
        """ Updates a Inventory to the database """
        if new_data.active != None:
            self.active = new_data.active
        self.quantity = new_data.quantity or self.quantity
        self.name = new_data.name or self.name
        self.reorder_quantity = new_data.reorder_quantity or self.reorder_quantity
        self.restock_level = new_data.restock_level or self.restock_level
        self.updated_at = datetime.utcnow()
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
            "restock_level": self.restock_level,
            "active": self.active
        }

    def deserialize(self, data):
        """ Wrapper for deserializing an Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            if not isinstance(data, dict):
                raise TypeError
            self.deserialize_util(data)
        except KeyError as error:
            raise DataValidationError(
                f'Invalid Inventory: missing {error.args[0]}'
            ) from error
        except TypeError as error:
            raise DataValidationError(
                f'Invalid Inventory: body of request contained bad or no data'\
                f'Error message: {error}'
            ) from error
        except ValueError as error:
            raise OutOfRangeError(
                f'Invalid Inventory: body of request contained values out of range'\
                f'Error message: {error}'
            ) from error
        return self

    def deserialize_util(self, data):
        """ Deserializing an Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        if data.get("name"):
            if isinstance(data.get("name"), str):
                self.name = data.get("name")
            else:
                raise TypeError

        if data.get("active") is not None:
            if isinstance(data.get("active"), bool):
                self.active = data.get("active")
            else:
                raise TypeError

        for field in ["quantity", "reorder_quantity", "restock_level"]:
            if data.get(field):
                if not isinstance(data.get(field), int):
                    raise TypeError
                if data.get(field) < 0:
                    raise ValueError
                setattr(self, field, data.get(field))

    def checkout(self, data):
        """ Checkout ordered_quantity from record

        Args:
            data (dict): A dictionary containing the resource data
        """
        ordered_quantity = data.get('ordered_quantity')
        try:
            if self.active == False:
                raise TypeError
            if ordered_quantity == None or type(ordered_quantity) is not int:
                raise DataValidationError
            if ordered_quantity > self.quantity:
                raise ValueError
        except ValueError as error:
            raise OutOfRangeError(f'Quantity specified ({ordered_quantity}) '
                f'is more than quantity of record ({self.quantity}).') from error
        except TypeError as error:
            raise InactiveRecordError('Record is inactive.') from error
        except DataValidationError as error:
            raise OutOfRangeError("Ordered quantity is missing or not int.") from error

        new_record = Inventory()
        new_record.quantity = self.quantity - ordered_quantity
        self.update(new_record)
    
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
    def find(cls, by_params):
        """ Finds a Inventory by it's ID and condition """
        by_id, by_condition = by_params
        logger.info("Processing lookup for id %s and condition %s ...", by_id, by_condition)
        return cls.query.get((by_id, by_condition))

    @classmethod
    def find_by_general_filter(cls, by_filters):
        """Returns all Inventories by all the filters
            :param by_filters: contains all the filter parameters and their values
            :type available: dictionary
            :return: a collection of Inventories that satisfy all the filter parameters
            :rtype: list
        """
        __query = db.session.query(cls)
        for attr, values in by_filters.items():
            if attr == "quantity":
                (value, oper) = values
                dict_oper = {
                    "=": getattr(cls, attr) == value, "<=": getattr(cls, attr) <= value,
                    ">=": getattr(cls, attr) >= value, "<": getattr(cls, attr) < value,
                    ">": getattr(cls, attr) > value
                    }
                try:
                    filt = dict_oper[oper]
                    __query = __query.filter(filt)
                except KeyError:
                    logger.info("Invalid operator %s ...", oper)
                    return "Invalid"
            else:
                __query = __query.filter(getattr(cls, attr) == values)
            # now we can run the query
        results = __query.all()
        return results
