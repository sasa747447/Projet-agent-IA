# Projet Agent IA Autonome

Agent IA autonome piloté par l'API Gemini, s'appuyant sur l'architecture du projet "Nettoyage IA".

## Modes d'exécution
* **Mode en ligne** : Piloté par Google Gemini pour l'analyse et l'envoi des commandes.

* **Mode local** : Propulsé par Ollama avec le modèle 'qwen2.5:7b-instruct', spécialement choisi pour sa rapidité d'exécution des commandes.

## Problématique actuelle
Une difficulté est rencontrée avec le mode local :

Le modèle a du mal à interpréter proprement les scans HTML transmis par le script Python.

Il génère des sélecteurs fantaisistes et inadaptés.

Il ne déclenche jamais la commande question lorsqu'il est bloqué, contrairement à Gemini.

_Est-ce une limitation des capacités de raisonnement de ce modèle local par rapport à Gemini, ou un problème d'optimisation du prompt ?_

## Module python requis :
*  msvcrt
*  json
*  shutil
*  subprocess
*  playwright
*  pathlib
*  google
*  ollama

## Structure du projet Final
```text
Projet-agent-IA/
│
├── Projet-agent-IA.py
└── Config/
    └── config.json
```

## Information a savoir
* **Panneau d'administration** : Tapez **`admin`** directement dans le terminal à la place d'une question pour l'IA pour accéder au panneau d'administration du programme.
* L'IA pourra vous poser des questions afin de préciser ses prochaines actions.

## Fonctionnement du programme

* **1.** Le dossier Config est vérifié, puis le programme s'assure que le fichier config.json y est présent.

* **2.** Si le fichier est manquant, le programme demande de saisir votre clé d'API Gemini, qui est obligatoire.

* **3.** Le programme vous invite ensuite à saisir votre consigne initiale.

* **4.** Votre réponse est prise en compte, et une première requête est envoyée à l'IA pour ouvrir le site internet.

* **5.** Un scan complet de la page est effectué pour extraire tous les textes, boutons et champs (input) sous forme textuelle.

* **6.** Une seconde requête est alors envoyée à l'IA en lui transmettant ce scan complet
  
* **7.** L'IA renvoie une série de commandes, par exemple : `lien+google.com | btn_id_class+btn_valider.`

* **8.** Le programme analyse la chaîne de caractères pour la découper en plusieurs parties à l'aide du séparateur |.

* **9.** Une boucle `for` analyse chaque partie de la commande pour préparer son exécution.

* **10.** `Playwright` entre en action pour cliquer, remplir ou exécuter les commandes sur la page.
  
* **11.** La boucle recommence à partir du scan de la page.


## Installation :
```bash
git clone https://github.com/sasa747447/Projet-agent-IA.git
cd Projet-agent-IA
python Projet-agent-IA.py
```
