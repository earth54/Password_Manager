"""Password manager that saves users/passwords into a MongoDB database
"""

import getpass
import os
import re
from utility import utility
from cryptography.fernet import Fernet
from typing import Any
from rich.console import Console
from rich.table import Table
import platform
import subprocess

console = Console()


def generate_user_fernet_key() -> Any:
    """Generates a unique Fernet key for the user

    Returns:
        Any: Returns the Fernet key
    """

    key = Fernet.generate_key()
    return key


def store_fernet_key_locally(fernet_key: Any, user_id: Any) -> None:
    """Stores the Fernet key locally for a user

    Args:
        fernet_key (Any): The Fernet key
        user_id (Any): Name of the user
    """

    key_filename = f"user_{user_id}_fernet.key"
    with open(key_filename, "wb") as key_file:
        key_file.write(fernet_key)


def load_fernet_key_locally(user_id: Any) -> Any:
    """Loads the user's Fernet key from local storage

    Args:
        user_id (Any): Name of the user

    Returns:
        Any: Fernet key stored locally on system
    """

    key_filename = f"user_{user_id}_fernet.key"
    with open(key_filename, "rb") as key_file:
        key = key_file.read()
    return key


def encrypt_password(fernet_key: Any, password: Any) -> Any:
    """Encrypts a password using Fernet key

    Args:
        fernet_key (Any): The Fernet key
        password (Any): user password

    Returns:
        bytes: The user's encrypted password
    """

    fernet = Fernet(fernet_key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password


def decrypt_password(fernet_key: Any, encrypted_password: Any) -> Any:
    """Decrypts user passwords

    Args:
        fernet_key (Any): Fernet key
        encrypted_password (Any): User's encrypted password

    Returns:
        Any: Decrypted user's password
    """

    fernet = Fernet(fernet_key)
    decrypted_password = fernet.decrypt(encrypted_password)
    return decrypted_password.decode()


def user_exists(username: str) -> Any:
    """Check if the username already exists

    Args:
        username (str): User's name

    Returns:
        Any: If username is not found, it returns none,
            else returns username
    """

    existing_user_M = utility.find_entries("users",
                                           "names", {'username': username})
    return existing_user_M is not None


def service_exists(username: str, service_name: str) -> Any:
    """Check if service name already exists

    Args:
        username (str): User's name
        service_name (str): The name of the website/service

    Returns:
        Any: If service name is found returns True else retrns False
    """

    existing_service = utility.find_entries("passwords",
                                            username,
                                            {'service_name': service_name})

    if existing_service:
        return True
    else:
        return False


def validate_master_password(password: Any) -> Any:
    """Validate master password strength

    Args:
        password (Any): User's master password

    Returns:
        Any: If the master password's strength meets
        requirements return True, else return False
    """

    if (
        len(password) >= 8
        and re.search(r'[A-Z]', password)
        and re.search(r'[a-z]', password)
        and re.search(r'\d', password)
        and re.search(r'[@#$%^&+=!]', password)
    ):
        return True
    return False


def create_user(username: str, master_password: Any) -> None:
    """Create a new user with password strength and
        matching confirmation if user is not already setup.

    Args:
        username (str): User's name
        master_password (Any): User's master password
    """

    query1 = {"username": username}
    existing_user = utility.find_entries("users", "names", query1)

    if existing_user:
        clear_screen()
        console.print(
            "[bold red underline]Username already exists. Please "
            "choose a different username.")

    else:

        fernet_key_M = generate_user_fernet_key()

        encrypted_master_password_M = encrypt_password(fernet_key_M,
                                                       master_password)

        query = ({"username": username,
                  "master_password": encrypted_master_password_M})

        utility.insert_entry("users", "names", query)

        store_fernet_key_locally(fernet_key_M, username)
        clear_screen()
        console.print("\n[bold green underline]User created successfully")


def authenticate_user(username: str, master_password: Any) -> Any:
    """Authenticate a user to log into the Password Manager

    Args:
        username (str): User's name
        master_password (Any): User's master password

    Returns:
        Any: If user or the user's fernet key doesn't exist
        return False, else return True
    """

    query = {"username": username}

    if os.path.exists(f"user_{username}_fernet.key"):

        query = {"username": username}

        resultMongo = utility.find_entries("users", "names", query)

        if resultMongo != []:

            encrypted_master_password_M = resultMongo[0]['master_password']

            object_id_M = resultMongo[0]['username']

            fernet_key_M = load_fernet_key_locally(
                object_id_M)

            decrypted_master_password_M = decrypt_password(
                fernet_key_M, encrypted_master_password_M)
            try:
                if master_password == decrypted_master_password_M:
                    return True
            except Exception as e:
                clear_screen()
                console.print("[bold red underline]Error during "
                              f"password decryption: {e}")

        return False

    else:
        return False


# Function to modify the user's master password


def update_user_master_password(username: str,
                                new_master_password: Any) -> Any:
    """Modify the user's master password

    Args:
        username (str): User's name
        new_master_password (Any): The new master password

    Returns:
        Any: If the user doesn't exist or new password does not
        meet strength requirements return False, else return True
    """

    if not user_exists(username):
        clear_screen()
        console.print("[bold red underline]User does not exist.")
        return False

    if not validate_master_password(new_master_password):
        clear_screen()
        console.print(
            "[bold red underline]New master password "
            "does not meet the strength requirements.")
        return False

    user_info_M = utility.find_entries("users", "names",
                                       {'username': username})

    fernet_key_M = load_fernet_key_locally(user_info_M[0]['username'])

    encrypted_new_master_password_M = encrypt_password(
        fernet_key_M, new_master_password)

    old_data = {'username': username,
                'master_password': user_info_M[0]['master_password']}
    new_data = {'username': username,
                'master_password': encrypted_new_master_password_M}
    utility.update_entry("users", "names", old_data, new_data)

    return True


def delete_user(username: str) -> Any:
    """Delete the user and their passwords

    Args:
        username (str): User's name

    Returns:
        Any: Returns True once the user and passwords have been deleted.
    """

    if not user_exists(username):
        clear_screen()
        console.print("[bold red underline]User does not exist.")
        return False

    utility.delete_collection("passwords", username)

    utility.delete_entry("users", "names", {'username': username})

    key_filename = f"user_{username}_fernet.key"
    if os.path.exists(key_filename):
        os.remove(key_filename)

    return True


def add_password(username: str, service_name: str, username_entry: str,
                 password_entry: str) -> Any:
    """Adds an entry into the Passsword Manager
       including Service name, Username, and password.

    Args:
        username (str): User's name
        service_name (str): Name of the website/service being added
        username_entry (str): Username for the website/service
        password_entry (str): Password for the website/service

    Returns:
        Any: If the user exists in the user table
        add the entry and return True, else return False
    """

    query1 = {"username": username}
    existing_user = utility.find_entries("users", "names", query1)

    if existing_user is not None:

        # Load the user's Fernet key
        fernet_key_M = load_fernet_key_locally(existing_user[0]['username'])

        # Encrypt the password entry using the user's Fernet key
        encrypted_password_entry_M = encrypt_password(
            fernet_key_M, password_entry)

        query = {"username": existing_user[0]['username'],
                 "service_name": service_name,
                 "username_entry": username_entry,
                 "password_entry": encrypted_password_entry_M}

        utility.insert_entry("passwords", existing_user[0]['username'], query)

        return True
    else:
        return False


def retrieve_passwords(username: str) -> None:
    """Retrieve password entries for a user

    Args:
        username (str): User's name
    """
    user_id_M = utility.find_entries("users", "names", {"username": username})

    if user_id_M is not None:
        entries_M = utility.find_entries("passwords", username)

        print()
        table = Table(title=f"Entries for {username} ")

        table.add_column("Service", justify="left", style="cyan", no_wrap=True)
        table.add_column("Username", style="magenta")
        table.add_column("Password", justify="left", style="green")

        fernet_key_M = load_fernet_key_locally(user_id_M[0]['username'])

        for entry in entries_M:
            decrypted_password_M = decrypt_password(fernet_key_M,
                                                    entry['password_entry'])

            table.add_row(entry['service_name'], entry['username_entry'],
                          decrypted_password_M)

        console.print(table)

        console.input(
            "[bold dodger_blue1 underline]Press enter to continue....")
        clear_screen()

    else:
        clear_screen()
        console.print("\n[bold red underline]No password entries found.")


def update_service(username: str, service_name: str, new_username: str,
                   new_password: str) -> Any:
    """Update the username and password for an existing service

    Args:
        username (str): User's name
        service_name (str): Name of website/service
        new_username (str): New username for website/service
        new_password (str): New password for website/service

    Returns:
        Any: If an existing entry was found for the website/service
        update the entry and return True, else return error message and False
    """

    user_id_M = utility.find_entries("users", "names", {"username": username})

    if user_id_M:
        fernet_key_M = load_fernet_key_locally(user_id_M[0]['username'])

        encrypted_new_password_M = encrypt_password(fernet_key_M, new_password)

        user_id_M = utility.find_entries("passwords", user_id_M[0]['username'],
                                         {"service_name": service_name})

        if user_id_M:
            old_data = {'service_name': service_name,
                        'username_entry': user_id_M[0]['username_entry'],
                        'password_entry': user_id_M[0]['password_entry']}
            new_data = {'service_name': service_name,
                        'username_entry': new_username,
                        'password_entry': encrypted_new_password_M}
            utility.update_entry("passwords",
                                 user_id_M[0]['username'], old_data, new_data)

            return True
        else:
            return False

    else:
        clear_screen()
        console.print("[bold red underline]User not found.")
        return False


def delete_service_and_passwords(username: str, service_name: str) -> Any:
    """Delete a service and its passwords

    Args:
        username (str): User's name
        service_name (str): Name of website/service

    Returns:
        Any: If no entries are found for that website/service
        return false, else delete the entry and return True
    """

    return_entry = service_exists(username, service_name)

    if return_entry is False:
        return False

    utility.delete_entry("passwords", username, {'service_name': service_name})

    return True


def print_welcome_box(console: Any) -> None:
    """Prints welcome box

    Args:
        console (_type_): Console is used for the rich library
    """

    width = 60

    console.print(f'[magenta]{"=" * width}')
    console.print(f'[magenta]{"="}{" " * (width - 2)}[magenta]{"="}')
    console.print(f'[magenta]{"="}{" " * 12}:smiley:[bold cyan underline] '
                  'Welcome to Your Password Manager![/bold cyan underline]'
                  f':smiley:{" " * 8}[magenta]{"="}')
    console.print(f'[magenta]{"="}{" " * 4}[cyan]Safely store and manage your '
                  f'passwords with ease.[/cyan]{" " * 5}[magenta]{"="}')
    console.print(f'[magenta]{"="}{" " * (width - 2)}[magenta]{"="}')
    console.print(f'[magenta]{"=" * width}')


def main_choice_two() -> None:
    """User login to the Password Manager. If successful a functionality
        menu appears. The user will get an message if unsuccessful.
    """
    clear_screen()
    username = console.input("\n[bold green underline]Enter your username: ")
    console.print("[bold green underline]Enter your master password: ")
    master_password = getpass.getpass("")
    if authenticate_user(username, master_password):
        clear_screen()
        console.print("\n[bold green underline]Login successful.")

        while True:
            console.print("\n[bold dodger_blue1 underline]User Menu")

            console.print("[cyan]1. Add Password Entry")
            console.print("[magenta]2. Retrieve Password Entries")
            console.print("[cyan]3. Update a Service username and password")
            console.print(
                "[magenta]4. Delete a Service and associated password")
            console.print("[cyan]5. Change Master Password")
            console.print("[magenta]6. Delete current User and passwords")
            console.print("[cyan]7. Logout")

            user_choice = console.input(
                "\n[bold dodger_blue1 underline]Enter your choice: ")

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
                break

            elif user_choice == "7":
                choice_seven()
                break

            else:
                clear_screen()
                console.print(
                    "[bold red underline]Invalid choice. "
                    "Please choose a valid option.")

    else:
        clear_screen()
        console.print("[bold red underline]Login failed. Please "
                      "check your username, master password, and fernet key.")


def choice_one(username: str) -> None:
    """Add new service and password

    Args:
        username (str): User's name
    """
    clear_screen()
    service_name = console.input(
        "\n[bold orange1 underline]Enter the service name: ")
    username_entry = console.input(
        "[bold orange1 underline]Enter the username: ")
    password_entry = console.input(
        "[bold orange1 underline]Enter the password: ")

    if add_password(username, service_name, username_entry,
                    password_entry):
        clear_screen()
        console.print(
            "\n[bold green underline]Password entry added successfully.")
    else:
        clear_screen()
        console.print(
            """[bold red underline]Failed to add password entry.
            Please create a user first.""")


def choice_two(username: str) -> None:
    """Display user's stored passwords

    Args:
        username (str): User's name
    """
    clear_screen()
    retrieve_passwords(username)


def choice_three(username: str) -> None:
    """Update Service username and password

    Args:
        username (str): User's name
    """
    clear_screen()
    service_name = console.input(
        "\n[bold orange1 underline]Enter the "
        "service name you want to update: ")
    new_username = console.input(
        "[bold orange1 underline]Enter the new username: ")
    new_password = console.input(
        "[bold orange1 underline]Enter the new password: ")
    # new_password = getpass.getpass(
    #     "Enter the new password: ")

    if update_service(username, service_name, new_username, new_password):
        clear_screen()
        console.print(
            f'\n[bold green underline]Password for {service_name} '
            'updated successfully.')
    else:
        clear_screen()
        console.print(
            '\n[bold red underline]Failed to update the password for '
            f'{service_name}. Service not found.')


def choice_four(username: str) -> None:
    """Delete Service and password

    Args:
        username (str): User's name
    """
    clear_screen()
    service_name = console.input(
        "\n[bold dodger_blue1 underline]Enter the "
        "service name you want to delete: ")
    confirmation = console.input(
        f"\n[bold red underline]Are you sure you want to delete the service"
        f" {service_name} and its associated password?"
        " (yes/no): ")

    if confirmation.lower() == "yes":
        return_entry = delete_service_and_passwords(username, service_name)
        if return_entry is True:
            clear_screen()
            console.print(
                f'[bold bright_yellow underline]Service {service_name} and '
                'its associated password deleted successfully.')
        else:
            clear_screen()
            console.print(
                f'[bold red underline]Failed to delete {service_name}.'
                ' Service not found.')
    else:
        clear_screen()
        console.print("[bold orange1 underline]Service deletion canceled.")


def choice_five(username: str) -> None:
    """Change master password

    Args:
        username (str): User's name
    """
    clear_screen()
    console.print("\n[bold orange1 underline]Enter your new master password: ")
    new_master_password = getpass.getpass("")

    if update_user_master_password(username, new_master_password):
        clear_screen()
        console.print(
            "\n[bold green underline]Master password modified successfully.")
    else:
        clear_screen()
        console.print(
            '\n[bold red underline]Failed to modify master password.'
            'Please create a user first.')


def choice_six(username: str) -> None:
    """Delete user and all passwords

    Args:
        username (str): User's name
    """
    clear_screen()
    confirmation = console.input(
        '\n[bold red underline]Are you sure you want to delete your user '
        'and all associated data? (yes/no): ')
    if confirmation.lower() == "yes":
        if delete_user(username):
            clear_screen()
            console.print(
                '\n[bold green underline]User and associated data'
                ' deleted successfully.')

        else:
            clear_screen()
            console.print(
                '\n[bold red underline]Failed to delete user.'
                'Please create a user first.')

    else:
        clear_screen()
        console.print("\n[bold orange1 underline]User deletion canceled.")


def choice_seven() -> None:
    """Logout of Password Manager
    """
    clear_screen()
    console.print("\n[bold green underline]Logout successful.")


def clear_screen() -> None:
    """Clears CLI screen
    """
    # For Windows
    if platform.system() == "Windows":
        subprocess.call('cls', shell=True)
    # For macOS and Linux
    else:
        subprocess.call('clear', shell=True)


def main() -> None:
    """Driver function to initiate the Password Manager
    """
    clear_screen()
    print_welcome_box(console)

    while True:
        console.print("\n[bold dodger_blue1 underline]Password Manager Menu")
        console.print("[cyan]1. Create User")
        console.print("[magenta]2. Login")
        console.print("[cyan]3. Exit")
        choice = console.input("\n[bold dodger_blue1 underline]Enter "
                               "your choice: ")

        if choice == "1":
            clear_screen()
            username = console.input(
                "\n[bold dodger_blue1 underline]Enter your username: ")

            console.print(
                "[bold dodger_blue1 underline]\nPassword must meet the "
                "following requirements:")
            console.print("[bold dark_cyan]- At least 8 characters long")
            console.print(
                "[bold dodger_blue1]- At least one uppercase letter (A-Z)")
            console.print(
                "[bold dark_cyan]- At least one lowercase letter (a-z)")
            console.print("[bold dodger_blue1]- At least one digit (0-9)")
            console.print(
                "[bold dark_cyan]- At least one special character (@#$%^&+=!)")

            console.print(
                "\n[bold dodger_blue1 underline]Enter your master password: ")
            master_password = getpass.getpass("")
            console.print(
                "\n[bold dodger_blue1 underline]Confirm your "
                "master password: ")
            confirm_password = getpass.getpass("")

            if master_password == confirm_password:
                if validate_master_password(master_password):
                    create_user(username, master_password)
                else:
                    clear_screen()
                    console.print(
                        "[bold red underline]Password does not meet "
                        "the strength requirements.")
            else:
                clear_screen()
                console.print(
                    "[bold red underline]Passwords do not match. "
                    "Please try again")

        elif choice == "2":
            main_choice_two()

        elif choice == "3":
            clear_screen()
            console.print("\n[bold green underline]Goodbye!\n")
            break

        else:
            clear_screen()
            console.print(
                "\n[bold red underline]Invalid choice. Please choose "
                "a valid option.")


if __name__ == "__main__":

    main()
