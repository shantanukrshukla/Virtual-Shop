import os
import logging
import configparser
import threading
from flask_restful import Resource, reqparse
from virtualshop.configuration import log_config
from virtualshop.sp_executor.sp_executor import SPExecutor
from virtualshop.datamodel.db_connector import database_access
from virtualshop.configuration.resource_encryption import FileDecrpytor

# Create a ConfigParser instance and read the config.ini file
config = configparser.ConfigParser()

#config.read(config_file_path)
decrypt_instance = FileDecrpytor()
conn = decrypt_instance.filedecrypt().decode('utf-8')
config.read_string(conn)
db_table_name = config.get('database', 'db_table_name')

# Logging initialization
logger = log_config.configure_logging()

# Create a custom filter to add the class name to the log record
class ClassNameFilter(logging.Filter):
    def __init__(self, name=""):
        super().__init__()
        self.class_name = name
    def filter(self, record):
        record.classname = self.class_name
        return True

class ShopValidation():
    current_directory = os.path.abspath(os.path.dirname(__file__))
    virtualshop_directory = os.path.join(current_directory, '..', '..', 'virtualshop')
    shopValidation = os.path.join(virtualshop_directory, "scripts/shopValidation.sql")
    shopCreation = os.path.join(virtualshop_directory, "scripts/shopCreation.sql")
    TABLE_NAME = db_table_name
    def __init__(self, username):
        self.username = username

    @classmethod
    def find_by_shopname(cls, shopname):
        logger.addFilter(ClassNameFilter(__class__.__name__))
        logger.info("Making a connection to the database")
        connection = database_access()
        cursor = connection.cursor()
        with open(ShopValidation.shopValidation, 'r') as sql_file:
            query = sql_file.read()
            logger.info("Checking if a shop is already exists in our database or not")
            query = query.format(table=cls.TABLE_NAME)
            logger.info("query = {}".format(query))
            cursor.execute(query, (shopname,))
            row = cursor.fetchone()
            if row:
                logger.info("Shop found, returning info")
                user = row
            else:
                user = None
        connection.close()
        return user


class ShopRegistration(Resource):
    TABLE_NAME = db_table_name
    parser = reqparse.RequestParser()
    parser.add_argument('sellerId', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('shopname', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('description', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('address', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('phonenumber', type=str, required=True, help="This field cannot be left blank!")
    parser.add_argument('GSTnumber', type=str, required=True, help="This field cannot be left blank!")
    # Create a logger for the thread
    def post(self):
        logger.addFilter(ClassNameFilter(__class__.__name__))
        logger.info(f"Thread {threading.current_thread().name}: Registering a Shop")
        data = ShopRegistration.parser.parse_args()
        generateUniqueShopCode = SPExecutor()
        shop_id = generateUniqueShopCode.generateUniqueShopCode()
        status = "under vertification"
        if ShopValidation.find_by_shopname(data['shopname']):
            logger.error("User with that username already exists")
            return {"message": "Shop is already exists."}, 400
        # Perform seller registration in a separate thread
        registration_thread = threading.Thread(target=self.register_shop, args=(shop_id, status, data))
        registration_thread.start()
        msg = f"Shop creation process started, status is in {status}."
        return {"message": msg}, 201

    def register_shop(self, shop_id, status, data):
        connection = database_access()
        cursor = connection.cursor()
        with open(ShopValidation.shopCreation, 'r') as sql_file:
            logger.info(f"creating new shop in our database with shopId : {shop_id}")
            query = sql_file.read()
            query = query.format(table=self.TABLE_NAME)
            cursor.execute(query, (shop_id, data['sellerId'], data['shopname'], data['description'], data['address'], data['phonenumber'], data['GSTnumber'], status))
            connection.commit()
        connection.close()
        logger.info("virtual shop has been created successfully")