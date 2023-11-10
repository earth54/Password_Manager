"""Module using APIs to communicate with MongoDB
"""


from pymongo import MongoClient
from pymongo import errors
from pymongo.server_api import ServerApi
from typing import Any, Dict

uri = "mongodb+srv://cluster1.cjufb6h.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
path_to_certificate = 'pm_cert.pem'


def create_connection() -> None:
    
    # Create a new client and connect to the server
    client = MongoClient(uri,tls=True,
            tlsCertificateKeyFile=path_to_certificate,
            server_api=ServerApi('1'))
    
    try:
        db = client['testDB']
        collection = db['testCol']
        doc_count = collection.count_documents({})
        print(doc_count)  # Should print 0 as the testDB doesn't exist
    except errors.ConnectionFailure as err:
        raise err
    

def create_collection(database_name: str, collection_name: str) -> None:
    
    client = MongoClient(uri, tls=True,
            tlsCertificateKeyFile=path_to_certificate,
            server_api=ServerApi('1'))

    try:
        db = client[database_name]
        db.create_collection(collection_name)
    except Exception as err:
        raise err
    
    
def insert_entry(database_name: str, collection_name: str, entry: Dict[str, Any]) -> None:
    
    client = MongoClient(uri, tls=True,
        tlsCertificateKeyFile=path_to_certificate,
        server_api=ServerApi('1'))
    
    try:
        db = client[database_name]
        collection = db[collection_name]
        collection.insert_one(entry)
    except Exception as err:
        raise err
    
    
def insert_entries(database_name: str, collection_name: str, entries: Dict[str, Any]) -> None:
    
    client = MongoClient(uri, tls=True,
        tlsCertificateKeyFile=path_to_certificate,
        server_api=ServerApi('1'))
    
    try:
        db = client[database_name]
        collection = db[collection_name]
        collection.insert_many(entries)
    except Exception as err:
        raise err    
    
    
def find_entries(database_name: str, collection_name: str, entries: Dict[str, Any] | None = None) -> None:
    
    client = MongoClient(uri, tls=True,
        tlsCertificateKeyFile=path_to_certificate,
        server_api=ServerApi('1'))
    
    try:
        if entries is None:
            db = client[database_name]
            collection = db[collection_name]
            cursor = collection.find()
        else:
            cursor = collection.find(entries)
        documents = list(cursor)
        return documents
    except Exception as err:
        raise err    
    
    
def update_entry(database_name: str, collection_name: str, old_data: Dict[str, Any], new_data: Dict[str, Any] ) -> None:
    
    client = MongoClient(uri, tls=True,
        tlsCertificateKeyFile=path_to_certificate,
        server_api=ServerApi('1'))
    
    try:
        db = client[database_name]
        collection = db[collection_name]
        updated_data = collection.update_one(old_data, {"$set": new_data})
        return updated_data.modified_count
    except Exception as err:
        raise err    
    

def update_entries(database_name: str, collection_name: str, old_data: Dict[str, Any], new_data: Dict[str, Any] ) -> None:
    
    client = MongoClient(uri, tls=True,
        tlsCertificateKeyFile=path_to_certificate,
        server_api=ServerApi('1'))
    
    try:
        db = client[database_name]
        collection = db[collection_name]
        updated_data = collection.update_many(old_data, {"$set": new_data})
        # return updated_data.modified_count
    except Exception as err:
        raise err    
    

def delete_entry(database_name: str, collection_name: str, old_data: Dict[str, Any]) -> None:
    
    client = MongoClient(uri, tls=True,
        tlsCertificateKeyFile=path_to_certificate,
        server_api=ServerApi('1'))
    
    try:
        db = client[database_name]
        collection = db[collection_name]
        result = collection.delete_one(old_data)
    except Exception as err:
        raise err    
    
    
def delete_entries(database_name: str, collection_name: str, old_data: Dict[str, Any]) -> None:
    
    client = MongoClient(uri, tls=True,
        tlsCertificateKeyFile=path_to_certificate,
        server_api=ServerApi('1'))
    
    try:
        db = client[database_name]
        collection = db[collection_name]
        result = collection.delete_many(old_data)
    except Exception as err:
        raise err   

    

    
if __name__ == "__main__":
    create_connection()





    








# import requests
# # import json
# from typing import Any, Dict



# # let's use API provided by Internation Space Station
# # http://api.open-notify.org/iss-now.json
# response = requests.get('http://api.open-notify.org/iss-now.json')
# print(response.json())


# end_point = 'https://us-east-1.aws.data.mongodb-api.com/app/data-nisvn/endpoint/data/v1/action'

# funct = 'find'

# uri = "mongodb+srv://cluster0.xeszaub.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"

# api_key = 'LFkYS0X0JeQT15CCgs1hsuIhrW4q3QCCHFRk50QkWH8fV0spYo44tdAQwNXgMea0'

# headers = {'Content-Type': 'application/json', 
#     'Access-Control-Request-Headers': '*',
#     'api-key': f'{api_key}'}

# session = requests.Session()


# session.headers.update(headers)


# payload = {
#     "dataSource": "Cluster1",
#     "database": "Password_Manager",
#     "collection": "sample_airbnb",
#     "filter": {
#         "name": "Ribeira Charming Duplex"
#         # '_id': res['insertedId']
#         # '_id': {'$oid': res['insertedId']}
#     }
# }


# def find_one(session: requests.Session, payload: Dict[str, Any]) -> Dict[str, Any]:
#     uri = f'{end_point}/find'
#     result = session.post(uri, json=payload)
#     return result


# rec = find_one(session, payload)

# print(rec.json())

# r = rec.json()['document']

# print(r)

# r['name']