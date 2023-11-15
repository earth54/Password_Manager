import sqlite3
import getpass
import os
import re
from cryptography.fernet import Fernet
from pymongo import MongoClient
from dotenv import load_dotenv


def setup_connection():
    # Load environment variables from a .env file
    load_dotenv()

    # Retrieve the MongoDB Atlas connection string from environment variables
    MONGODB_URI = os.getenv('MONGODB_URI')

    if not MONGODB_URI:
        raise ValueError(
            "MongoDB connection string not found in environment variables")

    # Assuming the '.pem' file is in the 'utility' folder within the same directory as the script
    # Gets the directory of the script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # The relative path to the '.pem' file
    pem_relative_path = 'utility/pm_cert.pem'
    # Full path to the '.pem' file
    pem_path = os.path.join(script_dir, pem_relative_path)

    # Connect to the MongoDB Atlas cluster with X.509 authentication
    client = MongoClient(MONGODB_URI,
                         tls=True,
                         tlsCertificateKeyFile=pem_path,
                         authMechanism='MONGODB-X509')

    # The database name is usually derived from the URI; otherwise, it can be set explicitly
    DB_NAME = os.getenv('DB_NAME') or 'your_default_db_name'
    db = client[DB_NAME]

    return client, db


# function to close the db connection when finished with the database operations
def close_connection(client):
    client.close()


def setup_database(db):
    # Define the 'Users' collection and create a unique index on the 'username' field
    users_collection = db['Users']
    users_collection.create_index([('username', 1)], unique=True)

    # Define the 'Passwords' collection and create an index on the 'user_id' field
    passwords_collection = db['Passwords']
    passwords_collection.create_index([('user_id', 1)])

    print("Database and collections are set up in MongoDB Atlas.")


# Generate a unique Fernet key for the user
def generate_user_fernet_key():
    key = Fernet.generate_key()
    return key

# Store the Fernet key locally for a user


def store_fernet_key_locally(fernet_key, user_id):
    key_filename = f"user_{user_id}_fernet.key"
    with open(key_filename, "wb") as key_file:
        key_file.write(fernet_key)

# Load the user's Fernet key from local storage


def load_fernet_key_locally(user_id):
    key_filename = f"user_{user_id}_fernet.key"
    with open(key_filename, "rb") as key_file:
        key = key_file.read()
    return key

# Encrypt a password using Fernet key


def encrypt_password(fernet_key, password):
    fernet = Fernet(fernet_key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password

# Function to decrypt passwords


def decrypt_password(fernet_key, encrypted_password):
    fernet = Fernet(fernet_key)
    decrypted_password = fernet.decrypt(encrypted_password)
    return decrypted_password.decode()

# Function to check if the username already exists


def user_exists(username):
    users_collection = db['Users']
    existing_user = users_collection.find_one({'username': username})
    return existing_user is not None

# Function to validate master password strength


def validate_master_password(password):
    if (
        len(password) >= 8
        and re.search(r'[A-Z]', password)
        and re.search(r'[a-z]', password)
        and re.search(r'\d', password)
        and re.search(r'[@#$%^&+=!]', password)
    ):
        return True
    return False

# Function to create a new user with password strength and matching confirmation


def create_user(db, username, master_password):
    users_collection = db['Users']

    # Check if the username already exists
    if user_exists(db, username):
        print("Username already exists. Please choose a different username.")
        return

    # Generate a unique Fernet key for the user
    fernet_key = generate_user_fernet_key()

    # Encrypt the master password using the user's Fernet key
    encrypted_master_password = encrypt_password(fernet_key, master_password)

    # Insert the new user document into the collection
    users_collection.insert_one({
        'username': username,
        'encrypted_master_password': encrypted_master_password
    })

    user_id = users_collection.find_one({'username': username})['_id']

    # Store the user's Fernet key locally
    store_fernet_key_locally(fernet_key, str(user_id))

    print("User created successfully")


# Function to authenticate a user


def authenticate_user(db, username, master_password):
    users_collection = db['Users']
    user_document = users_collection.find_one({'username': username})

    if user_document is not None:
        encrypted_master_password = user_document['encrypted_master_password']
        user_id = user_document['_id']

        fernet_key = load_fernet_key_locally(str(user_id))

        try:
            decrypted_master_password = decrypt_password(
                fernet_key, encrypted_master_password)
            return master_password == decrypted_master_password
        except Exception as e:
            print(f"Error during password decryption: {e}")

    return False


# Function to modify the user's master password


def update_user_master_password(db, username, new_master_password):
    if not validate_master_password(new_master_password):
        print("New master password does not meet the strength requirements.")
        return False

    users_collection = db['Users']
    user_document = users_collection.find_one({'username': username})

    if user_document:
        user_id = user_document['_id']
        fernet_key = load_fernet_key_locally(str(user_id))

        encrypted_new_master_password = encrypt_password(
            fernet_key, new_master_password)

        users_collection.update_one(
            {'_id': user_id},
            {'$set': {'encrypted_master_password': encrypted_new_master_password}}
        )

        return True
    else:
        print("User does not exist.")
        return False


# Function to delete the user and their passwords


def delete_user(db, username):
    users_collection = db['Users']
    passwords_collection = db['Passwords']

    user_document = users_collection.find_one({'username': username})
    if user_document:
        user_id = user_document['_id']

        # Delete the user's passwords
        passwords_collection.delete_many({'user_id': user_id})

        # Delete the user document from the Users collection
        users_collection.delete_one({'_id': user_id})

        # Remove the Fernet key file for this user
        key_filename = f"user_{user_id}_fernet.key"
        if os.path.exists(key_filename):
            os.remove(key_filename)

        print("User and associated data deleted successfully.")
        return True
    else:
        print("User not found.")
        return False


# Function to add a password entry for a user in MongoDB
def add_password(db, user_id, service_name, username_entry, password_entry):
    # Load the user's Fernet key
    fernet_key = load_fernet_key_locally(user_id)

    # Encrypt the password entry using the user's Fernet key
    encrypted_password_entry = encrypt_password(fernet_key, password_entry)

    # Get the Passwords collection
    passwords_collection = db['Passwords']

    # Insert the new password document into the Passwords collection
    passwords_collection.insert_one({
        'user_id': user_id,
        'service_name': service_name,
        'username': username_entry,
        'encrypted_password': encrypted_password_entry
    })
    print("Password entry added successfully.")
    return True


# Function to retrieve password entries for a user


# Function to retrieve password entries for a user in MongoDB
def retrieve_passwords(db, user_id):
    # Get the Passwords collection
    passwords_collection = db['Passwords']

    # Find all documents where the user_id matches
    password_documents = passwords_collection.find({'user_id': user_id})

    # Decrypt the encrypted password entries and display them
    fernet_key = load_fernet_key_locally(user_id)
    for doc in password_documents:
        decrypted_password = decrypt_password(
            fernet_key, doc['encrypted_password'])
        print(f"Service: {doc['service_name']}")
        print(f"Username: {doc['username']}")
        print(f"Password: {decrypted_password}")
        print()  # Add an empty line to separate entries


# Function to update the username and password for a service


# Function to update the username and password for a service in MongoDB
def update_service(db, user_id, service_name, new_username, new_password):
    # Get the Passwords collection
    passwords_collection = db['Passwords']

    # Load the user's Fernet key
    fernet_key = load_fernet_key_locally(user_id)

    # Encrypt the new username and password with the user's Fernet key
    encrypted_new_password = encrypt_password(fernet_key, new_password)

    # Update the username and password for the service
    result = passwords_collection.update_one(
        {'user_id': user_id, 'service_name': service_name},
        {'$set': {'username': new_username, 'encrypted_password': encrypted_new_password}}
    )

    if result.matched_count:
        print(f"Password for {service_name} updated successfully.")
        return True
    else:
        print(
            f"Failed to update the password for {service_name}. Service not found.")
        return False


# Function to delete a service and its passwords in MongoDB
def delete_service_and_passwords(db, user_id, service_name):
    # Get the Passwords collection
    passwords_collection = db['Passwords']

    # Delete the documents where the user_id and service_name match
    result = passwords_collection.delete_many(
        {'user_id': user_id, 'service_name': service_name})

    if result.deleted_count:
        print(f"{service_name} and its associated password deleted successfully.")
        return True
    else:
        print(f"Failed to delete {service_name}. Service not found.")
        return False


if __name__ == "__main__":
    # Setup the database connection
    client, db = setup_connection()
    setup_database(db)

    while True:
        print("Password Manager Menu")
        print("1. Create User")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("Enter your username: ")

            print("Password must meet the following requirements:")
            print("- At least 8 characters long")
            print("- At least one uppercase letter (A-Z)")
            print("- At least one lowercase letter (a-z)")
            print("- At least one digit (0-9)")
            print("- At least one special character (@#$%^&+=!)")

            master_password = getpass.getpass("Enter your master password: ")
            confirm_password = getpass.getpass(
                "Confirm your master password: ")

            if master_password == confirm_password:
                if validate_master_password(master_password):
                    create_user(username, master_password)
                else:
                    print("Password does not meet the strength requirements.")
            else:
                print("Passwords do not match. Please try again")

        elif choice == "2":
            username = input("Enter your username: ")
            master_password = getpass.getpass("Enter your master password: ")
            if authenticate_user(username, master_password):
                print("Login successful.")
                while True:
                    print("User Menu")
                    print("1. Add Password Entry")
                    print("2. Retrieve Password Entries")
                    print("3. Update a Service username and passsword")
                    print("4. Delete a Service and associated password")
                    print("5. Change Master Password")
                    print("6. Delete current User and passwords")
                    print("7. Logout")
                    user_choice = input("Enter your choice: ")

                    if user_choice == "1":
                        # Add new Service and password
                        service_name = input("Enter the service name: ")
                        username_entry = input("Enter the username: ")
                        password_entry = input("Enter the password: ")

                        if add_password(username, service_name, username_entry, password_entry):
                            print("Password entry added successfully.")
                        else:
                            print(
                                "Failed to add password entry. Please create a user first.")

                    elif user_choice == "2":
                        # Display user's stored passwords
                        entries = retrieve_passwords(username)
                        if entries:
                            for entry in entries:
                                print(f"Service: {entry[2]}")
                                print(f"Username: {entry[3]}")
                                print(f"Password: {entry[4]}")
                        else:
                            print("No password entries found.")

                    elif user_choice == "3":
                        # Update Service username and password
                        service_name = input(
                            "Enter the service name you want to update: ")
                        new_username = input("Enter the new username: ")
                        new_password = getpass.getpass(
                            "Enter the new password: ")

                        if update_service(username, service_name, new_username, new_password):
                            print(
                                f"Password for {service_name} updated successfully.")
                        else:
                            print(
                                f"Failed to update the password for {service_name}. Service not found.")

                    elif user_choice == "4":
                        # Delete Service and password
                        service_name = input(
                            "Enter the service name you want to delete: ")
                        confirmation = input(
                            f"Are you sure you want to delete the service '{service_name}' and its associated password? (yes/no): ")

                        if confirmation.lower() == "yes":
                            if delete_service_and_passwords(username, service_name):
                                print(
                                    f"{service_name} and its associated password deleted successfully.")
                            else:
                                print(
                                    f"Failed to delete {service_name}. Service not found.")
                        else:
                            print("Service deletion canceled.")

                    elif user_choice == "5":
                        # Change master password
                        new_master_password = getpass.getpass(
                            "Enter your new master password: ")

                        if update_user_master_password(username, new_master_password):
                            print("Master password modified successfully.")
                        else:
                            print(
                                "Failed to modify master password. Please create a user first.")

                    elif user_choice == "6":
                        # Delete user and all passwords
                        confirmation = input(
                            "Are you sure you want to delete your user and all associated data? (yes/no): ")
                        if confirmation.lower() == "yes":
                            if delete_user(username):
                                print(
                                    "User and associated data deleted successfully.")
                                break
                            else:
                                print(
                                    "Failed to delete user. Please create a user first.")
                                break
                        else:
                            print("User deletion canceled.")

                    elif user_choice == "7":
                        # Logout
                        print("Logout successful.")
                        break

                    else:
                        print("Invalid choice. Please choose a valid option.")

            else:
                print("Login failed. Please check your username and master password.")

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please choose a valid option.")
