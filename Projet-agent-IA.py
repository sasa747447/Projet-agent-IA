import os, sys, time, msvcrt, json, shutil
from playwright.sync_api import sync_playwright
from pathlib import Path
from google import genai

INSTRUCTION_IA = """
Tu est un assistant IA personelle qui aura pour but d'etre un agent IA
"""

dossier_config = Path(__file__).resolve().parent / "config"
fichier_config = dossier_config / "config.json"

def clear():
    os.system('cls')

def saisie_dynamique(invite="Entre ton texte : "):
    texte = ""

    sys.stdout.write(invite + "[  ]\b\b")
    sys.stdout.flush()

    while True:
        char = msvcrt.getch()
        if char in (b"\r", b"\n"):
            print()
            break
        elif char == b"\x08":
            if len(texte) > 0:
                texte = texte[:-1]
        else:
            try:
                texte += char.decode("utf-8")
            except UnicodeDecodeError:
                pass

        cols = shutil.get_terminal_size().columns
        marge = len(invite) + 5
        max_taille = cols - marge

        texte_affiche = texte if len(texte) < max_taille else texte[-max_taille:]
        ligne = f"\r{invite}[ {texte_affiche} ]"
        espaces_nettoyage = " " * max(0, cols - len(ligne) - 1)
        sys.stdout.write(ligne + espaces_nettoyage + "\b" * len(espaces_nettoyage) + "\b\b")
        sys.stdout.flush()

    return texte

def créer_json():
    clear()
    rps_api_key = saisie_dynamique("Entrez votre Api Key Gemini : ")
    donne_base_json = {
        "API_KEY" : rps_api_key,
        "model_IA" : "models/gemini-3.5-flash-lite"
    }
    fichier_config.write_text(json.dumps(donne_base_json, indent=4), encoding="utf-8")

if not dossier_config.exists():
    dossier_config.mkdir(parents=True, exist_ok=True)

if fichier_config.exists():
    config = json.loads(fichier_config.read_text(encoding="utf-8"))
else:
    créer_json()
    config = json.loads(fichier_config.read_text(encoding="utf-8"))

API_KEY = config.get("API_KEY")

try:
    client = genai.Client(api_key=API_KEY)
except Exception:
    client = None

if client:
    chat = client.chats.create(
    model=config.get('model_IA'),
    config={"system_instruction": INSTRUCTION_IA}
)

terminer = False

while not terminer:
    rps_utilisateur = saisie_dynamique("Que voulez vous faire : ")

    if not rps_utilisateur:
        continue

    if rps_utilisateur == "q":
        print("Fermeture du programme...")
        break

    else:
        rps_ia = chat.send_message(rps_utilisateur)
        print(f"[IA Réponse] : {rps_ia.text}")

    print("[Agent] Ouverture du navigateur pour exécuter l'action...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        url_ia = rps_ia.text.strip()
        page.goto(url_ia)

        while True:
            if page.is_closed():
                print("\n[Navigateur] Fenêtre fermée par l'utilisateur.")
                break

            if msvcrt.kbhit():
                try:
                    touche = msvcrt.getch().decode('utf-8')
                    if touche.lower() == "q":
                        browser.close()
                        break
                except UnicodeDecodeError:
                    pass
            
            time.sleep(0.1)