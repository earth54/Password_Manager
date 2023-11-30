"""Module using APIs to communicate with MongoDB
"""

from pymongo import MongoClient
from pymongo import errors
from pymongo.server_api import ServerApi
from pymongo.errors import OperationFailure
from typing import Any, Dict, List

uri = 'mongodb+srv://cluster1.cjufb6h.mongodb.net/?authSource=%24external'  \
<<<<<<< HEAD
        '&authMechanism=MONGODB-X509&retryWrites=true&w=majority'

path_to_certificate = 'pm_cert.pem'


def create_connection() -> Any:

=======
    '&authMechanism=MONGODB-X509&retryWrites=true&w=majority'

path_to_certificate = 'utility/pm_cert.pem'


def create_connection() -> int:
>>>>>>> issue/2
    """Creates connection to MongoDB database

    Raises:
        ex: Raises an error if found
    """

    client = MongoClient(uri, tls=True,
                         tlsCertificateKeyFile=path_to_certificate,
                         server_api=ServerApi('1'))   # type: Any

    try:
        db = client['testDB']
        collection = db['testCol']
        doc_count = collection.count_documents({})
<<<<<<< HEAD
        print(doc_count)  # Should print 0 as the testDB doesn't exist
=======
        return doc_count  # Should print 0 as the testDB doesn't exist
>>>>>>> issue/2
    except errors.ConnectionFailure as ex:
        print(ex)
        raise ex


def create_collection(database_name: str,
<<<<<<< HEAD
                      collection_name: str) -> None:
=======
                      collection_name: str) -> str:
>>>>>>> issue/2

    """Creates a collection

    Args:
        database_name (str): Name of MongoDB database
        collection_name (str): Name of MongoDB collection

    Raises:
        ex: Raises an error if found
    """

    client = MongoClient(uri, tls=True,
                         tlsCertificateKeyFile=path_to_certificate,
                         server_api=ServerApi('1'))   # type: Any

    try:
        db = client[database_name]
        db.create_collection(collection_name)
<<<<<<< HEAD
=======
        return db.list_collection_names()
>>>>>>> issue/2
    except OperationFailure as ex:
        print(ex)
        raise ex


def insert_entry(database_name: str,
<<<<<<< HEAD
                 collection_name: str, entry: List[Any]) -> None:

=======
                 collection_name: str, entry: Dict[str, Any]) -> None:
>>>>>>> issue/2
    """Inserts one {key: value} pair into collection

    Args:
        database_name (str): Name of MongoDB database
        collection_name (str): Name of MongoDB collection
        entry (list[str, Any]): A single {key: value} listing to insert into
            the collection

    Raises:
        ex: Raises an error if found
    """

    client = MongoClient(uri, tls=True,
                         tlsCertificateKeyFile=path_to_certificate,
                         server_api=ServerApi('1'))   # type: Any

    try:
        db = client[database_name]
        collection = db[collection_name]
<<<<<<< HEAD
        result = collection.insert_one(entry)
        print(result.inserted_id)  # prints inserted _id
=======
        collection.insert_one(entry)
>>>>>>> issue/2
    except OperationFailure as ex:
        print(ex)
        raise ex


def insert_entries(database_name: str, collection_name: str,
                   entries: List[Any]) -> None:
<<<<<<< HEAD

=======
>>>>>>> issue/2
    """Inserts mutltiple {key: value} entries into collection as long as they
        are in a list

    Args:
        database_name (str): Name of MongoDB database
        collection_name (str): Name of MongoDB collection
        entries (list[Any, Any]): List of the {key: value} pairs to insert
            into the collection

    Raises:
        ex: Raises an error if found
    """

    client = MongoClient(uri, tls=True,
                         tlsCertificateKeyFile=path_to_certificate,
                         server_api=ServerApi('1'))   # type: Any

    try:
        db = client[database_name]
        collection = db[collection_name]
<<<<<<< HEAD
        result = collection.insert_many(entries)
        print(result.inserted_ids)  # prints inserted _ids
=======
        collection.insert_many(entries)
>>>>>>> issue/2
    except OperationFailure as ex:
        print(ex)
        raise ex


def find_entries(database_name: str, collection_name: str,
                 entries: Dict[str, Any] | None = None) -> Any:
<<<<<<< HEAD

=======
>>>>>>> issue/2
    """Finds {key: value} listings in a collection

    Args:
        database_name (str): Name of MongoDB database
        collection_name (str): Name of MongoDB collection
        entries (Dict[str, Any] | None, optional): If variable name "entries"
            is not passed in, the function will find and return all listings in
            the collection.
            If variable name "entries" is passed in, the function will search
            for matching keys in {key: value} filter and return all matching
            listings in the collection.
        Variable name "entries" defaults to None.

    Raises:
        ex: Raises an error if found

    Returns:
        Any: Returns list of collection dictionary entries
    """

    client = MongoClient(uri, tls=True,
                         tlsCertificateKeyFile=path_to_certificate,
                         server_api=ServerApi('1'))   # type: Any

    try:
        if entries is None:
            db = client[database_name]
            collection = db[collection_name]
            cursor = collection.find()
            documents = list(cursor)
            return documents

        else:
            db = client[database_name]
            collection = db[collection_name]
            cursor = collection.find(entries)
            documents = list(cursor)
            return documents
    except OperationFailure as ex:
        print(ex)
        raise ex


def update_entry(database_name: str, collection_name: str,
                 old_data: Dict[str, Any], new_data: Dict[str, Any]) -> None:
<<<<<<< HEAD

=======
>>>>>>> issue/2
    """Finds the first matching key of {key: value} filter and
        updates the value

    Args:
        database_name (str): Name of MongoDB database
        collection_name (str): Name of MongoDB collection
        old_data (Dict[str, Any]): The {key: value} filter that needs to be
            removed from the first matching entry
        new_data (Dict[str, Any]): the {key: value} filter that needs to take
            the place of the first matching {key:value} filter in
            the collection

    Raises:
        ex: Raises an error if found
    """

    client = MongoClient(uri, tls=True,
                         tlsCertificateKeyFile=path_to_certificate,
                         server_api=ServerApi('1'))   # type: Any

    try:
        db = client[database_name]
        collection = db[collection_name]
<<<<<<< HEAD
        updated_data = collection.update_one(old_data, {"$set": new_data})
        # prints the number of {key: value} affected
        print(updated_data.modified_count)
=======
        collection.update_one(old_data, {"$set": new_data})
>>>>>>> issue/2
    except OperationFailure as ex:
        print(ex)
        raise ex


def update_entries(database_name: str, collection_name: str,
                   old_data: Dict[str, Any], new_data: Dict[str, Any]) -> None:
<<<<<<< HEAD

=======
>>>>>>> issue/2
    """Finds the all matching keys of {key: value} filter and updates the
        values

    Args:
        database_name (str): Name of MongoDB database
        collection_name (str): Name of MongoDB collection
        old_data (Dict[str, Any]): The {key: value} filter that needs to be
            removed from the collection
        new_data (Dict[str, Any]): the {key: value} filter that needs to take
            the place of all removed {key:value} in the collection

    Raises:
        ex: Raises an error if found
    """

    client = MongoClient(uri, tls=True,
                         tlsCertificateKeyFile=path_to_certificate,
                         server_api=ServerApi('1'))   # type: Any

    try:
        db = client[database_name]
        collection = db[collection_name]
<<<<<<< HEAD
        updated_data = collection.update_many(old_data, {"$set": new_data})
        # prints the number of {key: value} pairs affected
        print(updated_data.modified_count)
=======
        collection.update_many(old_data, {"$set": new_data})
>>>>>>> issue/2
    except OperationFailure as ex:
        print(ex)
        raise ex


def delete_entry(database_name: str, collection_name: str,
                 old_data: Dict[str, Any]) -> None:
<<<<<<< HEAD

=======
>>>>>>> issue/2
    """Deletes the first matching {key: value} filter entry

    Args:
        database_name (str): Name of MongoDB database
        collection_name (str): Name of MongoDB collection
        old_data (Dict[str, Any]): The {key: value} filter you want to delete
        from the first matching entry in the collection

    Raises:
        ex: Raises an error if found
    """

    client = MongoClient(uri, tls=True,
                         tlsCertificateKeyFile=path_to_certificate,
                         server_api=ServerApi('1'))   # type: Any

    try:
        db = client[database_name]
        collection = db[collection_name]
<<<<<<< HEAD
        result = collection.delete_one(old_data)
        print(result.deleted_count)  # prints the number of deleted entries
=======
        collection.delete_one(old_data)
>>>>>>> issue/2
    except OperationFailure as ex:
        print(ex)
        raise ex


def delete_entries(database_name: str, collection_name: str,
                   old_data: Dict[str, Any]) -> None:
<<<<<<< HEAD

=======
>>>>>>> issue/2
    """Deletes entries matching {key: value} filter

    Args:
        database_name (str): Name of MongoDB database
        collection_name (str): Name of MongoDB collection
        old_data (Dict[str, Any]): The {key: value} filter you want to delete
        from all entries in the collection

    Raises:
        ex: Raises an error if found
    """

    client = MongoClient(uri, tls=True,
                         tlsCertificateKeyFile=path_to_certificate,
                         server_api=ServerApi('1'))   # type: Any

    try:
        db = client[database_name]
        collection = db[collection_name]
<<<<<<< HEAD
        result = collection.delete_many(old_data)
        print(result.deleted_count)  # prints the number of deleted entries
=======
        collection.delete_many(old_data)
    except OperationFailure as ex:
        print(ex)
        raise ex


def delete_collection(database_name: str, collection_name: str) -> None:
    """Deletes a collection

    Args:
        database_name (str): Name of MongoDB database
        collection_name (str): Name of MongoDB collection

    Raises:
        ex: Raises an error if found
    """

    client = MongoClient(uri, tls=True,
                         tlsCertificateKeyFile=path_to_certificate,
                         server_api=ServerApi('1'))   # type: Any

    try:
        db = client[database_name]
        collection = db[collection_name]
        collection.drop()
>>>>>>> issue/2
    except OperationFailure as ex:
        print(ex)
        raise ex
