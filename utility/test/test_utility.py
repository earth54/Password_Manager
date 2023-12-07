"""
Test module for utility.py
"""

import unittest
from utility import utility


class TestUtility(unittest.TestCase):

    def setUp(self) -> None:
        """Setup if needed
        """
        # Create a mock MongoDB server
        pass

    def tearDown(self) -> None:
        """Teardown if needed
        """
        # Clean up resources if needed
        pass

    def test_create_connection(self) -> None:
        """Tests a created Mongodb connection
        """

        doc_count = utility.create_connection()

        # If the connection was sucessful it should return 0
        # as no 'testDB' or 'testCol' exist
        self.assertEqual(doc_count, 0)

    def test_create_collection(self) -> None:
        """Tests a created Mongodb collection
        """
        database = "test_database"
        collection = "test_collection"

        names = utility.create_collection(database, collection)

        self.assertEqual(names, [collection])
        utility.delete_collection(database, collection)

    def test_insert_entry(self) -> None:
        """Tests an inserted entry into a Mongodb collection
        """
        database = "test_database"
        collection = "test_collection"

        entry = {'name': 'John Doe', 'email': 'john@example.com'}
        utility.insert_entry(database, collection, entry)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[0]['name'], 'John Doe')
        self.assertEqual(inserted_entry[0]['email'], 'john@example.com')

        utility.delete_collection(database, collection)

    def test_insert_entries(self) -> None:
        """Tests interted entries into a Mongodb collection
        """
        database = "test_database"
        collection = "test_collection"

        entry = [{'name': 'John Doe', 'email': 'john@example.com'},
                 {'name': 'John Q Public', 'email': 'The_Public@example.com'},
                 {'name': 'The Sheriff', 'email': 'Sheriff@example.com'}
                 ]
        utility.insert_entries(database, collection, entry)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[0]['name'], 'John Doe')
        self.assertEqual(inserted_entry[1]['email'], 'The_Public@example.com')
        self.assertEqual(inserted_entry[2]['email'], 'Sheriff@example.com')

        utility.delete_collection(database, collection)

    def test_find_entries(self) -> None:
        """Tests to find an entry and entries in a Mongodb collection
        """
        database = "test_database"
        collection = "test_collection"

        entry = [{'name': 'John Doe', 'email': 'john@example.com'},
                 {'name': 'John Q Public', 'email': 'Public@example.com'},
                 {'name': 'The Sheriff', 'email': 'Sheriff@example.com'}
                 ]
        utility.insert_entries(database, collection, entry)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[1]['name'], 'John Q Public')
        self.assertEqual(inserted_entry[2]['email'], 'Sheriff@example.com')

        get_entry = {'email': 'john@example.com'}
        inserted_entry = utility.find_entries(database, collection, get_entry)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[0]['name'], 'John Doe')

        utility.delete_collection(database, collection)

    def test_update_entry(self) -> None:
        """Tests to update an entry in a Mongodb collection
        """
        database = "test_database"
        collection = "test_collection"

        old_data = {'name': 'Mac Truck', 'email': 'MT@example.com'}
        utility.insert_entry(database, collection, old_data)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[0]['name'], 'Mac Truck')
        self.assertEqual(inserted_entry[0]['email'], 'MT@example.com')

        new_data = {'name': 'Kenworth Truck', 'email': 'KT@example.com'}
        utility.update_entry(database, collection, old_data, new_data)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[0]['name'], 'Kenworth Truck')
        self.assertEqual(inserted_entry[0]['email'], 'KT@example.com')

        utility.delete_collection(database, collection)

    def test_update_entries(self) -> None:
        """Tests to update entries in a Mongodb collection
        """
        database = "test_database"
        collection = "test_collection"

        entry = [{'name': 'John Doe', 'email': 'john@example.com'},
                 {'name': 'John Q Public', 'email': 'john@example.com'},
                 {'name': 'The Sheriff', 'email': 'john@example.com'}
                 ]
        utility.insert_entries(database, collection, entry)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[1]['email'], 'john@example.com')
        self.assertEqual(inserted_entry[2]['email'], 'john@example.com')

        old_data = {'email': 'john@example.com'}
        new_data = {'email': 'Wick@example.com'}
        utility.update_entries(database, collection, old_data, new_data)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[0]['email'], 'Wick@example.com')
        self.assertEqual(inserted_entry[1]['email'], 'Wick@example.com')
        self.assertEqual(inserted_entry[2]['email'], 'Wick@example.com')

        utility.delete_collection(database, collection)

    def test_delete_entry(self) -> None:
        """Test to delete an entry in a Mongodb collection
        """
        database = "test_database"
        collection = "test_collection"

        entry = [{'name': 'John Doe', 'email': 'john@example.com'},
                 {'name': 'John Q Public', 'email': 'jqpublic@example.com'},
                 {'name': 'The Sheriff', 'email': 'Sheriff@example.com'}
                 ]
        utility.insert_entries(database, collection, entry)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[1]['email'], 'jqpublic@example.com')
        self.assertEqual(inserted_entry[2]['email'], 'Sheriff@example.com')

        old_data = {'email': 'jqpublic@example.com'}

        utility.delete_entry(database, collection, old_data)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[0]['email'], 'john@example.com')
        self.assertEqual(inserted_entry[1]['email'], 'Sheriff@example.com')

        utility.delete_collection(database, collection)

    def test_delete_entries(self) -> None:
        """Test to delete entries in a Mongodb collection
        """
        database = "test_database"
        collection = "test_collection"

        entry = [{'name': 'John Doe', 'email': 'john@example.com'},
                 {'name': 'John Q Public', 'email': 'jqpublic@example.com'},
                 {'name': 'The Sheriff', 'email': 'john@example.com'}
                 ]
        utility.insert_entries(database, collection, entry)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[1]['email'], 'jqpublic@example.com')
        self.assertEqual(inserted_entry[2]['email'], 'john@example.com')

        old_data = {'email': 'john@example.com'}

        utility.delete_entries(database, collection, old_data)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[0]['email'], 'jqpublic@example.com')

        utility.delete_collection(database, collection)

    def test_delete_collection(self) -> None:
        """Test to delete a collection in Mongodb
        """
        database = "test_database"
        collection = "test_collection"

        entry = [{'name': 'John Doe', 'email': 'john@example.com'},
                 {'name': 'John Q Public', 'email': 'jqpublic@example.com'},
                 {'name': 'The Sheriff', 'email': 'Sheriff@example.com'}
                 ]
        utility.insert_entries(database, collection, entry)

        inserted_entry = utility.find_entries(database, collection)

        self.assertIsNotNone(inserted_entry)
        self.assertEqual(inserted_entry[1]['email'], 'jqpublic@example.com')
        self.assertEqual(inserted_entry[2]['email'], 'Sheriff@example.com')

        utility.delete_collection(database, collection)

        inserted_entry = utility.find_entries(database, collection)

        self.assertEqual(inserted_entry, [])
