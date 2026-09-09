import os, sys, time, msvcrt, json, shutil
from playwright.sync_api import sync_playwright
from pathlib import Path
from google import genai

INSTRUCTION_IA = """
Tu es un assistant IA personnel agissant comme un agent d'automatisation web (Playwright).
Voici les règles EXTRÊMEMENT IMPORTANTES à suivre à la lettre :
- Tu dois TOUJOURS commencer par donner un lien à ouvrir avec la commande 'lien' mais tu ne dois rien mettre ensuite apres la commande lien.
- Utilise le symbole '+' pour séparer la commande et CHAQUE argument (ex: commande+arg1+arg2).
- Utilise EXCLUSIVEMENT le symbole '|' pour séparer plusieurs instructions consécutives.
- N'utilise JAMAIS de caractères jokers ou d'étoiles '*'.
- Ne réponds QUE par la suite de commandes. Aucun texte explicatif, aucune intro, aucune politesse.

SYNTAXES STRICTEMENT AUTORISÉES (N'en invente AUCUNE autre) :
  • lien + <url_complete>
  • btn_class_id + <selecteur_css> (ex: .ma-classe ou #mon-id)
  • btn_titre + <texte_du_bouton_ou_lien>
  • input + <selecteur_css> + <texte_a_ecrire>
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

def complement_boucle():
    while True:
        if msvcrt.getch().decode("utf-8").lower() == "q":
            browser.close()
            break
        time.sleep(0.1)

def scan_environement(page):
    return page.evaluate("""() => {
        let info = [];
        document.querySelectorAll('button, a, input, textarea, [role="button"]').forEach(el => {
            if (el.offsetParent !== null) {
                let tag = el.tagName.toLowerCase();
                if (tag === 'button') tag = 'btn';
                else if (tag === 'input') tag = 'in';
                else if (tag === 'textarea') tag = 'txt';
                else if (tag === 'a') tag = 'lnk';
                
                let texte = (el.innerText || el.value || el.placeholder || '').trim().substring(0, 20);
                let id = el.id ? `#${el.id}` : '';
                let classe = el.className ? `.${el.className.split(' ').join('.')}` : '';
                
                if (texte || el.id || el.className) {
                    info.push(`[${tag}] "${texte}" ${id} ${classe}`.trim());
                }
            }
        });
        return info.join('\\n');
    }""")

def ouvrire_site(chaine_ia):
    if chaine_ia.strip().startswith('lien+'):
        chaine_ia = chaine_ia.replace("lien+", "", 1)
    page.goto(chaine_ia)

def executer_commande(chaine_ia):

    if not chaine_ia or chaine_ia.strip() == "":
        print("Aucune instruction à exécuter.")
        return

terminer_ia = False

while not terminer:
    clear()
    rps_utilisateur = saisie_dynamique("Que voulez vous faire")

    if not rps_utilisateur or rps_utilisateur.strip() == "":
        continue

    if rps_utilisateur.lower().strip() == "q":
        print("Fermeture du programme...")
        break

    rps_ia_ouverture_site = chat.send_message(f"C'est votre premier fois. Demande utilisateur : {rps_utilisateur}")
    print(f"Page ouvert : {rps_ia_ouverture_site.text}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        ouvrire_site(rps_ia_ouverture_site.text)

        while not terminer_ia:
            page.wait_for_load_state("networkidle")
            resultat_scan = scan_environement(page)
            print(resultat_scan)
            msvcrt.getch()