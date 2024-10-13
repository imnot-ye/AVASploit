import colorama
from colorama import Fore, Style
from BruteForceWebLogin.webLogin import startCredBruteForce
import asyncio

def print_header():
    colorama.init(autoreset=True)
    print(Fore.WHITE + "    ___ _    _____   _____       __      _ __ ")
    print(Fore.WHITE + "   /   | |  / /   | / ___/____  / /___  (_) /_")
    print(Fore.WHITE + "  / /| | | / / /| | \\__ \\/ __ \\/ / __ \\/ / __/")
    print(Fore.WHITE + " / ___ | |/ / ___ |___/ / /_/ / / /_/ / / /_  ")
    print(Fore.WHITE + "/_/  |_|___/_/  |_/____/ .___/_/\\____/_/\\__/  ")
    print(Fore.WHITE + "                      /_/                     ")

def print_menu():
    # Stampa il menu
    print(Fore.WHITE + Style.BRIGHT + "╔════════════════════════════════╗")
    print(Fore.WHITE + Style.BRIGHT + "║        WELCOME TO " + Fore.RED + "AVASploit" + Fore.WHITE + "    ║")  # Solo AVASploit in rosso
    print(Fore.WHITE + Style.BRIGHT + "╠════════════════════════════════╣")
    
    # Colore giallo solo per i numeri
    print(Fore.WHITE + Style.BRIGHT + "║ " + '\033[38;5;178m' + "[1]" + Fore.WHITE + " - WebLogin                 ║")  # Giallo per il numero 1
    print(Fore.WHITE + Style.BRIGHT + "║ " + '\033[38;5;178m' + "[2]" + Fore.WHITE + " - SQLi Login               ║")  # Giallo per il numero 2
    print(Fore.WHITE + Style.BRIGHT + "║ " + '\033[38;5;178m' + "[3]" + Fore.WHITE + " - Options                  ║")  # Giallo per il numero 3
    print(Fore.WHITE + Style.BRIGHT + "╚════════════════════════════════╝")
    print()

def handle_choice(choice):
    if choice == '1':
        print(Fore.GREEN + "You selected WebLogin!")
        asyncio.run(startCredBruteForce())
    elif choice == '2':
        print(Fore.GREEN + "You selected SQLi Login!")
        # Codice per SQLi Login
    elif choice == '3':
        print(Fore.GREEN + "You selected Options!")
        # Codice per le opzioni
    else:
        print(Fore.RED + "Invalid choice, please try again.")

# Funzione principale
def main():
    print_header()  # Mostra la scritta in stile ASCII
    while True:
        print_menu()
        choice = input(Fore.YELLOW + "Select an option (1-3): ")
        handle_choice(choice)
        if choice in ['1', '2', '3']:
            break  # Termina il loop se una scelta valida è stata effettuata

if __name__ == "__main__":
    main()
