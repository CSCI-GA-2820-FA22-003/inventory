"""
Models for YourResourceModel

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class Inventory(db.Model):
    """
    Class that represents a Inventory
    """

    class Status(enum.Enum):
        NEW = "new"
        REFURBISHED = "refurbished"
        RETURN = "return"

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(63), nullable=False)
    category = db.Column(db.String(63), nullable=False)
    status = db.Column(enum.Enum(Status), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return "<Inventory %r id=[%s]>" % (self.item, self.id)

    def create(self):
        """
        Creates a YourResourceModel to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a YourResourceModel to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a YourResourceModel from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a YourResourceModel into a dictionary """
        return {"id": self.id, "name": self.name}

    def deserialize(self, data):
        """
        Deserializes a YourResourceModel from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: body of request contained bad or no data - "
                "Error message: " + error
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the YourResourceModels in the database """
        logger.info("Processing all YourResourceModels")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a YourResourceModel by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all YourResourceModels with the given name

        Args:
            name (string): the name of the YourResourceModels you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
