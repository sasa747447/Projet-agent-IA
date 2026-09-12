import os, sys, time, msvcrt, json, shutil, winsound, subprocess
from playwright.sync_api import sync_playwright
from pathlib import Path
from google import genai
import ollama as ol

INSTRUCTION_IA = """
Tu es un assistant IA personnel agissant comme un agent d'automatisation web (Playwright). Tu réponds UNIQUEMENT par une commande, sans aucun texte explicatif, intro ou politesse.

RÈGLES D'EXÉCUTION :
1. PREMIER TOUR : Renvoie UNIQUEMENT 'lien+URL' (ex: lien+https://www.google.com). INTERDICTION absolue d'utiliser le symbole '|' ou d'autres commandes au premier tour.
2. TOURS SUIVANTS : Utilise les autres commandes selon le scan de la page.
3. SYNTAXE : Utilise '+' pour séparer la commande et CHAQUE argument (ex: commande+arg1+arg2). N'utilise JAMAIS d'étoiles '*' ou de caractères jokers.
4. ÉLÉMENTS INTROUVABLES : N'invente rien. Si un élément n'est pas dans le scan, gère ce qui est visible (pop-ups, cookies) ou attends.
5. Si on te demand d'accepter les cookie ou autre dis toujours OUI en cliquant sur le bouton
6. Si le sélecteur ou l'élément demandé n'apparaît pas dans le texte du scan actuel, tu n'as pas le droit de l'utiliser.

RÈGLE ANTI-BOUCLE & LIENS :
- Si l'URL actuelle du navigateur commence par 'http' (la page est déjà ouverte), tu as STRICTEMENT INTERDICTION d'utiliser la commande 'lien'. Passe directement à l'action suivante (ex: cliquer sur les cookies).

OBÉISSANCE ET SÉCURITÉ :
- Interdiction formelle de "faire ta vie" ou d'inventer des actions hors sujet.
- EN CAS DE DOUTE : Si tu hésites, si un élément est ambigu, ou si la page d'accueil/recherche est atteinte sans consigne précise, tu as l'OBLIGATION d'utiliser la commande 'question' (ex: question+Que dois-je chercher ?). Ne tape jamais du texte au hasard dans les champs.
- Si tu as des question pour paar exemple quoi chrcehr une adress mail mot de passe etc alors tu peut demander avec input+<ce que tu veut>
- Exemple valide : btn_class_id+#gb_6 | delay+2000 | input+.gb_Aa+MonTexte

SYNTAXES STRICTEMENT AUTORISÉES (NTERDICTION STRICTE d'inventer un autre nom de commande) :
  • lien + <url_complete>
  • btn_class_id + <selecteur_css> (ex: .ma-classe ou #mon-id)
  • input + <selecteur_css> + <texte_a_ecrire>
  • delay + <temps>
  • question + <texte_a_poser_a_l_utilisateur>
  • end
"""

MODEL_NOM_OLLAMA = "qwen2.5:7b-instruct"

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
        "model_IA" : "models/gemini-3.5-flash-lite",
        "automatique" : False,
        "DEV_MODE" : True,
        "IA_LOCAL_LIGNE": "LIGNE"
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
    chat_gemini = client.chats.create(
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
        // On cible les éléments interactifs ET les balises de texte (p, h1-h6, span, div textuels)
        document.querySelectorAll('button, a, input, textarea, [role="button"], p, h1, h2, h3, h4, h5, h6').forEach(el => {
            if (el.offsetParent !== null) {
                let tag = el.tagName.toLowerCase();
                if (tag === 'button') tag = 'btn';
                else if (tag === 'input') tag = 'in';
                else if (tag === 'textarea') tag = 'txt';
                else if (tag === 'a') tag = 'lnk';
                else if (tag.startsWith('h')) tag = 'hdr';
                
                let texte = (el.innerText || el.value || el.placeholder || '').trim().substring(0, 40);
                let id = el.id ? `#${el.id}` : '';
                let classe = el.className && typeof el.className === 'string' ? `.${el.className.split(' ').join('.')}` : '';
                
                if (texte || el.id || el.className) {
                    info.push(`[${tag}] "${texte}" ${id} ${classe}`.trim());
                }
            }
        });
        return info.join('\\n');
    }""")

_memoire_ollama = []

_memoire_ollama = []

def send_message_ollama(texte):
    global _memoire_ollama

    _memoire_ollama.append({"role": "user", "content": texte})

    messages = [{"role": "system", "content": INSTRUCTION_IA}] + _memoire_ollama

    try:
        response = ol.chat(model=MODEL_NOM_OLLAMA, messages=messages)
    except Exception:
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        response = ol.chat(model=MODEL_NOM_OLLAMA, messages=messages)

    reponse_content = response['message']['content']

    _memoire_ollama.append({"role": "assistant", "content": reponse_content})

    return reponse_content

terminer_admin = False

def mode_admin():
    global terminer_admin
    while not terminer_admin:
        clear()
        print("Mode Admin (taper 'q' pour quitter)")
        print("-"*30)
        print(f"1 : {'Desactiver' if config.get('automatique') else 'Activer'} le mode automatique")
        print(f"2 : {'Desactiver' if config.get('DEV_MODE') else 'Activer'} le DEV MODE")
        print(f"3 : Changer le model d'IA        [ Actuelle : {config.get('model_IA')}]")
        rps_admin = msvcrt.getch().decode('utf-8')

        if rps_admin == '1':
            clear()
            print("1 : Activer")
            print("2 : Desactiver")
            rps_mode_automatique = msvcrt.getch().decode('utf-8')

            if rps_mode_automatique == '1':
                config['automatique'] = True
            elif rps_mode_automatique == '2':
                config['automatique'] = False

            fichier_config.write_text(json.dumps(config, indent=4), encoding='utf-8')

        elif rps_admin == '2':
            clear()
            print("1 : Activer")
            print("2 : Desactiver")
            rps_DEV_MODE = msvcrt.getch().decode('utf-8')
            
            if rps_DEV_MODE == '1':
                config['DEV_MODE'] = True
            elif rps_DEV_MODE == '2':
                config['DEV_MODE'] = False

            fichier_config.write_text(json.dumps(config, indent=4), encoding='utf-8')

        elif rps_admin == '3':
            clear()
            model_dispo = {
                "models/gemini-3.5-flash-lite": " 🚀 Ultra-rapide | Recommandé #1 (500 req/jour)",
                "models/gemini-3.1-flash-lite": " 🚀 Instantané | Backup rapide (500 req/jour)",
                "models/gemini-3.6-flash":       " 🧠 Top intelligence Flash (20 req/jour)",
                "models/gemini-3.5-flash":       " 🎯 Précis pour dossiers complexes (20 req/jour)",
                "models/gemini-3-flash":         " ⚡ Rapide et logique (20 req/jour)",
                "models/gemini-2.5-flash":       " ⚡ Stable et rapide (20 req/jour)",
                "models/gemini-2.5-flash-lite":  " 🚀 Léger / Réserve (20 req/jour)",
                "models/gemini-3.1-pro":         " 🧠 Raisonnement avancé & Custom Tools",
                "gemma-4-31b-it":                  " 💥 Modèle 31B puissant (14,4k req/jour)",
                "gemma-4-26b-it":                  " 💥 Modèle 26B hyper rapide (14,4k req/jour)",
            }

            print(f"--- 🤖 MODÈLES DISPONIBLES --- [ Actuelle : {config.get('model_IA')} ]\n")
            for i, m in enumerate(model_dispo, 1):
                print(f"{i} : {m}")
            choix_model_ia = saisie_dynamique("\nVotre choix (numéro) : ")

            if choix_model_ia.isdigit() and 1 <= int(choix_model_ia) <= len(model_dispo):
                config['model_IA'] == model_dispo[int(choix_model_ia) - 1]
                fichier_config.write_text(json.dumps(config, indent=4), encoding="utf-8")
                print(f"\n[Succès] Modèle mis à jour : {config['model_IA']}")

        elif rps_admin == 'q':
            terminer_admin = True


def ouvrire_site(chaine_ia, page_obj):
    chaine_ia = chaine_ia.strip()
    if chaine_ia.startswith('lien+'):
        chaine_ia = chaine_ia.replace("lien+", "", 1).strip()
    elif chaine_ia.startswith('lien '):
        chaine_ia = chaine_ia.replace("lien ", "", 1).strip()

    if not chaine_ia.startswith('http'):
        chaine_ia = f"https://{chaine_ia}"
        
    page_obj.goto(chaine_ia)

def executer_commande(chaine_ia):
    if not chaine_ia or chaine_ia.strip() == "":
        print("Aucune instruction à exécuter.")
        return

    commande_separes = chaine_ia.split('|')

    for commande_separe in commande_separes:
        commande_separe = commande_separe.strip()
        if not commande_separe:
            continue

        parties = commande_separe.split('+')
        commande = parties[0].strip()

        try:
            if commande == 'lien' and len(parties) > 1:
                page.goto(parties[1].strip())

            elif commande == 'btn_class_id' and len(parties) > 1:
                selecteur = parties[1].strip()
                page.eval_on_selector(selecteur, "el => el.click()")

            elif commande == 'input' and len(parties) > 2:
                page.fill(parties[1].strip(), parties[2].strip())

            elif commande == 'delay' and len(parties) > 1:
                time.sleep(float(parties[1].strip()))

            if commande == "question" and len(parties) > 1:
                winsound.MessageBeep(winsound.MB_ICONERROR)
                print(f"\n[Question de l'IA] : {parties[1].strip()}")
                reponse_utilisateur = saisie_dynamique("Votre réponse : ")

                if config.get('IA_LOCAL_LIGNE') == "LIGNE":
                    chat_gemini.send_message(f"Réponse de l'utilisateur à votre question : {reponse_utilisateur}")
                elif config.get('IA_LOCAL_LIGNE') == "LOCAL":
                    send_message_ollama(f"Réponse de l'utilisateur à votre question : {reponse_utilisateur}")

            elif commande == 'end':
                print("Cliquer sur une touche pour continuer")
                msvcrt.getch()
                global terminer_ia
                terminer_ia = True
                print("Fin du programme")
                
            print(f"[Succès] Action exécutée : {commande}")
            
        except Exception as e:
            print(nic := f"[Attention] Impossible d'exécuter '{commande}' pour l'instant : {e}")
            print("-> L'agent ignorera cette action et réessaiera au prochain tour.")

        page.wait_for_timeout(1500)

terminer_ia = False

while not terminer:
    clear()
    rps_utilisateur = saisie_dynamique("Que voulez vous faire")

    if rps_utilisateur == "admin":
        mode_admin()
        continue

    if not rps_utilisateur or rps_utilisateur.strip() == "":
        continue

    if rps_utilisateur.lower().strip() == "q":
        print("Fermeture du programme...")
        break

    terminer_ia = False

    if config.get("IA_LOCAL_LIGNE") == "LIGNE":
        rps_ia_ouverture_site = chat_gemini.send_message(f"C'est la première fois. Demande utilisateur : {rps_utilisateur}. Rappelle-toi : donne UNIQUEMENT la commande lien+URL, rien d'autre.")
    elif config.get('IA_LOCAL_LIGNE') == "LOCAL":
        rps_ia_ouverture_site = send_message_ollama(f"C'est la première fois. Demande utilisateur : {rps_utilisateur}. Rappelle-toi : donne UNIQUEMENT la commande lien+URL, rien d'autre.")

    print(f"Page ouvert : {rps_ia_ouverture_site.text if config.get('IA_LOCAL_LIGNE') == 'LIGNE' else rps_ia_ouverture_site}") if config.get('DEV_MODE') else None

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, 
            slow_mo=500,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars"
            ]
            )
        page = browser.new_page(viewport=None)
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        ouvrire_site(rps_ia_ouverture_site.text if config.get('IA_LOCAL_LIGNE') == 'LIGNE' else rps_ia_ouverture_site, page)

        while not terminer_ia:
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
            resultat_scan = scan_environement(page)
            print(resultat_scan + "\n")  if config.get('DEV_MODE') else ""

            if config.get("IA_LOCAL_LIGNE") == "LIGNE":
                rps_scan_ia = chat_gemini.send_message("Scan complet : " + resultat_scan + ". Demande utilisateur" + rps_utilisateur)
            elif config.get('IA_LOCAL_LIGNE') == "LOCAL":
                rps_scan_ia = send_message_ollama("Scan complet : " + resultat_scan + ". Demande utilisateur" + rps_utilisateur)

            print(rps_scan_ia.text if config.get("IA_LOCAL_LIGNE") == "LIGNE" else rps_scan_ia)  if config.get('DEV_MODE') else ""

            executer_commande(rps_scan_ia.text if config.get("IA_LOCAL_LIGNE") == "LIGNE" else rps_scan_ia)

            if config.get('automatique'):
                print("Cliquer sur une touche pour continuer")
                msvcrt.getch()