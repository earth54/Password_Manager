"""
Test module for db.py
"""


# import os
import utility
# from utility import insert_entry
import unittest
from pymongo import MongoClient
# from pymongo.server_api import ServerApi
# from typing import Any

# from mongomock import MongoClient as MockMongoClient

# from typing import Tuple

# https://pytest-mock-resources.readthedocs.io/en/latest/mongo.html
# https://pytest-mock-resources.readthedocs.io/en/stable/quickstart.html#installation
# https://pytest-mock-resources.readthedocs.io/en/latest/mongo.html

# https://stackoverflow.com/questions/15753390/how-can-i-mock-requests-and-the-response

uri = 'mongodb+srv://cluster1.cjufb6h.mongodb.net/?authSource=%24external'  \
        '&authMechanism=MONGODB-X509&retryWrites=true&w=majority'

path_to_certificate = 'pm_cert.pem'


class TestDB(unittest.TestCase):
    """Test class for db.py
    """

    def setUp(self) -> None:
        """Set up a test database and collection
        """

        self.client = MongoClient()
        self.db = self.client['test_database']
        self.collection = self.db['test_collection']

    def tearDown(self) -> None:
        """Clean up after each test
        """
        self.client.drop_database('test_database')

    def test_insert_entry(self) -> str:

        # client = MongoClient(uri, tls=True,
        #                      tlsCertificateKeyFile=path_to_certificate,
        #                      server_api=ServerApi('1'))   # type: Any

        # Test the insert_document function
        database_name = "test_database"
        # db = client[database_name]
        collection_name = "test_collection"
        # collection = db[collection_name]
        data = {'name': 'John', 'age': 30}

        inserted_id = utility.insert_entry(database_name, collection_name,
                                           data)

        # Check if the document is inserted into the test collection
        document = self.collection.find_one({'_id': inserted_id})
        self.assertIsNotNone(document)
        self.assertEqual(document['name'], 'John')
        self.assertEqual(document['age'], 30)

    def test() -> None:
        pass
