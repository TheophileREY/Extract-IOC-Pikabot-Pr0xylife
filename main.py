import re
import requests
import datetime
import os


# RegEx pour les differents types d'IOC
ip_regex = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
hash_regex = r"\b[a-fA-F0-9]{32}\b|\b[a-fA-F0-9]{64}\b"
fqdn_regex = r"\b(?:(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,6})\b"


# Download le rapport de Pr0xylife
def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'w') as file:
            file.write(response.text)
    else:
        print("Fichier non trouve.")
        return None
    return filename


# Extraire les IOC du rapport de Pr0xylife
def extract_ioc(filename, date_str, single_file=False):
    with open(filename, 'r') as file:
        content = file.read()

    # Trouver les correspondances
    ips = re.findall(ip_regex, content)
    hashes = re.findall(hash_regex, content)
    fqdns = re.findall(fqdn_regex, content)

    # Filtre pour exclure les noms de fichiers detectes comme FQDN (avec les extensions)
    file_extension_regex = r"\.(exe|pdf|docx|jpg|png|csv|txt|js|dat)$" # A COMPLETER
    fqdns = [fqdn for fqdn in fqdns if not re.search(file_extension_regex, fqdn)]
    if single_file:
        # Exporter en un seul fichier
        with open(f"IOC_Pikabot_{date_str}.txt", 'w') as file:
            # Ecrire les hash
            file.write("---------- Hash ----------\n")
            for hash in sorted(set(hashes)):
                file.write(hash + '\n')

            # Ecrire les IP
            file.write("\n---------- IP ----------\n")
            for ip in sorted(set(ips)):
                file.write(ip + '\n')

            # Ecrire les FQDN
            file.write("\n---------- FQDN ----------\n")
            for fqdn in sorted(set(fqdns)):
                file.write(fqdn + '\n')
    else:
        # Exporter en plusieurs fichiers
        with open(f"ip_pikabot_{date_str}.txt", 'w') as file:
            file.write('\n'.join(sorted(set(ips))))
        with open(f"hash_pikabot_{date_str}.txt", 'w') as file:
            file.write('\n'.join(sorted(set(hashes))))
        with open(f"fqdn_pikabot_{date_str}.txt", 'w') as file:
            file.write('\n'.join(sorted(set(fqdns))))


# Menu principal
def main_menu():
    print("1. Recuperer le fichier du jour")
    print("2. Recuperer un fichier à une date specifiee")
    print("3. Analyser un fichier specifique (il devra porter le nom 'AnalysePikabot.txt' et etre dans le meme repertoire que le script")

    choice = input("Entrez votre choix (1, 2 ou 3): ")
    date_str = None 

    if choice == "1":
        today = datetime.datetime.now().strftime("%d.%m.%Y")
        url = f"https://github.com/pr0xylife/Pikabot/raw/main/Pikabot_{today}.txt"
        filename = download_file(url, f"Pikabot_{today}.txt")
        date_str = today 

    elif choice == "2":
        date_input = input("Entrez la date au format JJ/MM/AAAA: ")
        try:
            date_obj = datetime.datetime.strptime(date_input, "%d/%m/%Y")
            date_str = date_obj.strftime("%d.%m.%Y")  # Met à jour date_str
            url = f"https://github.com/pr0xylife/Pikabot/raw/main/Pikabot_{date_str}.txt"
            filename = download_file(url, f"Pikabot_{date_str}.txt")
        except ValueError:
            print("Format de date incorrect.")
            return  # Sortir de la fonction si la date est incorrecte

    elif choice == "3":
        if os.path.isfile("AnalysePikabot.txt"):
            filename = "AnalysePikabot.txt"
            date_str = "analyse"  
        else:
            print("Fichier AnalysePikabot.txt non trouve.")
            return  # Sortir de la fonction si le fichier n'est pas trouve

    else:
        print("Choix non valide.")
        return  # Sortir de la fonction si le choix n'est pas valide

    if filename and date_str:
        export_choice = input("Exporter en un seul fichier ? (Oui/Non): ")
        single_file = export_choice.lower() == "oui"
        extract_ioc(filename, date_str, single_file=single_file)


main_menu()
