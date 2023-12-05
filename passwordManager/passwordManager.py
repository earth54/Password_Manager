import sqlite3
import getpass
import os
import re
from cryptography.fernet import Fernet
from typing import Any

# Function to create the database and tables


def setup_database() -> None:
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            encrypted_master_password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Passwords (
            password_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            service_name TEXT NOT NULL,
            username TEXT NOT NULL,
            encrypted_password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Generate a unique Fernet key for the user


def generate_user_fernet_key() -> Any:
    key = Fernet.generate_key()
    return key

# Store the Fernet key locally for a user


def store_fernet_key_locally(fernet_key: Any, user_id: Any) -> Any:
    key_filename = f"user_{user_id}_fernet.key"
    with open(key_filename, "wb") as key_file:
        key_file.write(fernet_key)

# Load the user's Fernet key from local storage


def load_fernet_key_locally(user_id: Any) -> Any:
    key_filename = f"user_{user_id}_fernet.key"
    with open(key_filename, "rb") as key_file:
        key = key_file.read()
    return key

# Encrypt a password using Fernet key


def encrypt_password(fernet_key: Any, password: Any) -> Any:
    fernet = Fernet(fernet_key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password

# Function to decrypt passwords


def decrypt_password(fernet_key: Any, encrypted_password: Any) -> Any:
    fernet = Fernet(fernet_key)
    decrypted_password = fernet.decrypt(encrypted_password)
    return decrypted_password.decode()

# Function to check if the username already exists


def user_exists(username: str) -> Any:
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE username=?", (username,))
    existing_user = cursor.fetchone()
    conn.close()
    return existing_user is not None

# Function to validate master password strength


def validate_master_password(password: Any) -> Any:
    if (
        len(password) >= 8
        and re.search(r'[A-Z]', password)
        and re.search(r'[a-z]', password)
        and re.search(r'\d', password)
        and re.search(r'[@#$%^&+=!]', password)
    ):
        return True
    return False

# Function to create a new user with password strength
# and matching confirmation


def create_user(username: str, master_password: Any) -> None:

    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT user_id FROM Users WHERE username=?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        print("Username already exists. Please choose a different username.")
        conn.close()

    else:

        # Generate a unique Fernet key for the user
        fernet_key = generate_user_fernet_key()

        # Encrypt the master password using the user's Fernet key
        encrypted_master_password = encrypt_password(fernet_key,
                                                     master_password)

        cursor.execute("""INSERT INTO Users (username,
                    encrypted_master_password) VALUES (?, ?)""", (
                        username, encrypted_master_password))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Store the user's Fernet key locally
        store_fernet_key_locally(fernet_key, user_id)

        print("User created successfully")

# Function to authenticate a user


def authenticate_user(username: str, master_password: Any) -> Any:
    with sqlite3.connect('password_manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT encrypted_master_password, user_id FROM Users
            WHERE username=?""", (username,))
        result = cursor.fetchone()

    if result is not None:
        encrypted_master_password = result[0]
        user_id = result[1]  # Retrieve the user_id separately

        fernet_key = load_fernet_key_locally(
            user_id)  # Load the user's Fernet key

        try:
            # Decrypt the stored master password using the user's Fernet key
            decrypted_master_password = decrypt_password(
                fernet_key, encrypted_master_password)
            if master_password == decrypted_master_password:
                return True
        except Exception as e:
            print(f"Error during password decryption: {e}")

    return False

# Function to modify the user's master password


def update_user_master_password(username: str,
                                new_master_password: Any) -> Any:
    if not user_exists(username):
        print("User does not exist.")
        return False

    if not validate_master_password(new_master_password):
        print("New master password does not meet the strength requirements.")
        return False

    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()

    # Retrieve the user's current Fernet key
    cursor.execute(
        """SELECT user_id, encrypted_master_password
        FROM Users WHERE username=?""", (username,))
    user_info = cursor.fetchone()
    user_id = user_info[0]
    encrypted_master_password = user_info[1]

    # Decrypt the old master password
    fernet_key = load_fernet_key_locally(user_id)
    old_master_password = decrypt_password(
        fernet_key, encrypted_master_password)
    print(old_master_password)

    # Encrypt the new master password with the same key
    encrypted_new_master_password = encrypt_password(
        fernet_key, new_master_password)

    # Update the user's master password in the database
    cursor.execute("""UPDATE Users SET encrypted_master_password=?
                   WHERE user_id=?""", (encrypted_new_master_password,
                                        user_id))
    conn.commit()
    conn.close()

    return True

# Function to delete the user and their passwords


def delete_user(username: str) -> Any:
    if not user_exists(username):
        print("User does not exist.")
        return False

    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()

    # Retrieve the user's user_id
    cursor.execute("SELECT user_id FROM Users WHERE username=?", (username,))
    user_id = cursor.fetchone()[0]

    # Delete the user's passwords
    cursor.execute("DELETE FROM Passwords WHERE user_id=?", (user_id,))

    # Delete the user from the Users table
    cursor.execute("DELETE FROM Users WHERE username=?", (username,))

    conn.commit()
    conn.close()

    # Remove the Fernet key file for this user (optional)
    key_filename = f"user_{user_id}_fernet.key"
    if os.path.exists(key_filename):
        os.remove(key_filename)

    return True


def add_password(username: str, service_name: str , username_entry: str,
                 password_entry: str) -> Any:
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE username=?", (username,))
    user_id = cursor.fetchone()

    if user_id is not None:
        # Load the user's Fernet key
        fernet_key = load_fernet_key_locally(user_id[0])

        # Encrypt the password entry using the user's Fernet key
        encrypted_password_entry = encrypt_password(fernet_key, password_entry)

        cursor.execute("""INSERT INTO Passwords (user_id, service_name,
                       username, encrypted_password) VALUES (?, ?, ?, ?)""",
                       (user_id[0], service_name, username_entry,
                        encrypted_password_entry))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

# Function to retrieve password entries for a user


def retrieve_passwords(username: str) -> Any:
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE username=?", (username,))
    user_id = cursor.fetchone()

    if user_id is not None:
        cursor.execute(
            "SELECT * FROM Passwords WHERE user_id=?", (user_id[0],))
        entries = cursor.fetchall()

        # Load the user's Fernet key
        fernet_key = load_fernet_key_locally(user_id[0])

        # Decrypt the encrypted password entries and display them
        for entry in entries:
            decrypted_password = decrypt_password(fernet_key, entry[4])
            print(f"\nService: {entry[2]}")
            print(f"Username: {entry[3]}")
            print(f"Password: {decrypted_password}")
            print()  # Add an empty line to separate entries

        conn.close()
    else:
        conn.close()
        print("No password entries found.")

# Function to update the username and password for a service


def update_service(username: str, service_name: str, new_username: str,
                   new_password: str) -> Any:
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()

    # Check if the user exists
    cursor.execute("SELECT user_id FROM Users WHERE username=?", (username,))
    user_id = cursor.fetchone()

    if user_id:
        # Load the user's Fernet key
        fernet_key = load_fernet_key_locally(user_id[0])

        # Encrypt the new username and password with the user's Fernet key
        encrypted_new_password = encrypt_password(fernet_key, new_password)

        # Update the username and password for the service
        cursor.execute("""UPDATE Passwords SET username=?, encrypted_password=?
                       WHERE user_id=? AND service_name=?""",
                       (new_username, encrypted_new_password, user_id[0],
                        service_name))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        print("User not found.")
        return False


# Function to delete a service and its passwords
def delete_service_and_passwords(username: str, service_name: str) -> Any:
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()

    if not user_exists(username):
        conn.close()
        print("User not found.")
        return False

    # Delete the service and its associated passwords
    cursor.execute(
        """DELETE FROM Passwords WHERE user_id=(SELECT user_id FROM Users
        WHERE username=?) AND service_name=?""", (username, service_name))
    conn.commit()
    conn.close()
    return True


def main_choice_two() -> None:
    username = input("\nEnter your username: ")
    master_password = getpass.getpass("Enter your master password: ")
    if authenticate_user(username, master_password):
        print("\nLogin successful.")
        while True:
            print("\nUser Menu")
            print("1. Add Password Entry")
            print("2. Retrieve Password Entries")
            print("3. Update a Service username and passsword")
            print("4. Delete a Service and associated password")
            print("5. Change Master Password")
            print("6. Delete current User and passwords")
            print("7. Logout")
            user_choice = input("\nEnter your choice: ")

            if user_choice == "1":
                choice_one(username)

            elif user_choice == "2":
                choice_two(username)

            elif user_choice == "3":
                choice_three(username)

            elif user_choice == "4":
                choice_four(username)

            elif user_choice == "5":
                choice_five(username)

            elif user_choice == "6":
                choice_six(username)

            elif user_choice == "7":
                choice_seven()
                break

            else:
                print("Invalid choice. Please choose a valid option.")

    else:
        print("""Login failed. Please check your username
                and master password.""")


def choice_one(username: str) -> None:
    # Add new Service and password
    service_name = input("\nEnter the service name: ")
    username_entry = input("Enter the username: ")
    password_entry = input("Enter the password: ")

    if add_password(username, service_name, username_entry,
                    password_entry):
        print("\nPassword entry added successfully.")
    else:
        print(
            """Failed to add password entry.
            Please create a user first.""")


def choice_two(username: str) -> None:
    # Display user's stored passwords
    # entries = retrieve_passwords(username)
    retrieve_passwords(username)
    # if entries:
    #     for entry in entries:
    #         print(f"Service: {entry[2]}")
    #         print(f"Username: {entry[3]}")
    #         print(f"Password: {entry[4]}")
    # else:
    #     print("No password entries found.\n")


def choice_three(username: str) -> None:
    # Update Service username and password
    service_name = input(
        "\nEnter the service name you want to update: ")
    new_username = input("Enter the new username: ")
    new_password = getpass.getpass(
        "Enter the new password: ")

    if update_service(username, service_name, new_username, new_password):
        print(
            f"""\nPassword for {service_name}
            updated successfully.""")
    else:
        print(
            f"""\nFailed to update the password for
            {service_name}. Service not found.""")


def choice_four(username: str) -> None:
    # Delete Service and password
    service_name = input(
        "\nEnter the service name you want to delete: ")
    confirmation = input(
        f"\nAre you sure you want to delete the service"
        f" {service_name}' and its associated password?"
        " (yes/no): ")

    if confirmation.lower() == "yes":
        if delete_service_and_passwords(username,
                                        service_name):
            print(
                f"""{service_name} and its associated
                password deleted successfully.""")
        else:
            print(
                f"""Failed to delete {service_name}.
                Service not found.""")
    else:
        print("Service deletion canceled.")


def choice_five(username: str) -> None:
    # Change master password
    new_master_password = getpass.getpass(
        "\nEnter your new master password: ")

    if update_user_master_password(username, new_master_password):
        print("\nMaster password modified successfully.")
    else:
        print(
            """\nFailed to modify master password.
            Please create a user first.""")


def choice_six(username: str) -> None:
    # Delete user and all passwords
    confirmation = input(
        """\nAre you sure you want to delete your user
        and all associated data? (yes/no): """)
    if confirmation.lower() == "yes":
        if delete_user(username):
            print(
                """\nUser and associated data
                deleted successfully.""")

        else:
            print(
                """\nFailed to delete user.
                Please create a user first.""")

    else:
        print("\nUser deletion canceled.")


def choice_seven() -> None:
    # Logout
    print("\nLogout successful.")


if __name__ == "__main__":
    setup_database()

    while True:
        print("\nPassword Manager Menu")
        print("1. Create User")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("\nEnter your username: ")

            print("\nPassword must meet the following requirements:")
            print("- At least 8 characters long")
            print("- At least one uppercase letter (A-Z)")
            print("- At least one lowercase letter (a-z)")
            print("- At least one digit (0-9)")
            print("- At least one special character (@#$%^&+=!)")

            master_password = getpass.getpass("\nEnter your master password: ")
            confirm_password = getpass.getpass(
                "\nConfirm your master password: ")

            if master_password == confirm_password:
                if validate_master_password(master_password):
                    create_user(username, master_password)
                else:
                    print("Password does not meet the strength requirements.")
            else:
                print("Passwords do not match. Please try again")

        elif choice == "2":
            main_choice_two()

        elif choice == "3":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid choice. Please choose a valid option.")
