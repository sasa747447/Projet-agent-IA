# Projet Agent IA Autonome

Agent IA autonome piloté par l'API Gemini, s'appuyant sur l'architecture du projet "Nettoyage IA".

**Modes d'exécution**
* **Mode en ligne** : Piloté par Google Gemini pour l'analyse et l'envoi des commandes.

* **Mode local** : Propulsé par Ollama avec le modèle 'qwen2.5:7b-instruct', spécialement choisi pour sa rapidité d'exécution des commandes.

**Problématique actuelle**
Une difficulté est rencontrée avec le mode local :

Le modèle a du mal à interpréter proprement les scans HTML transmis par le script Python.

Il génère des sélecteurs fantaisistes et inadaptés.

Il ne déclenche jamais la commande question lorsqu'il est bloqué, contrairement à Gemini.

_Est-ce une limitation des capacités de raisonnement de ce modèle local par rapport à Gemini, ou un problème d'optimisation du prompt ?_

**Module python requis :**
*  msvcrt
*  json
*  shutil
*  subprocess
*  playwright
*  pathlib
*  google
*  ollama

**Structure du projet Final**
```text
Projet-agent-IA/
│
├── Projet-agent-IA.py
└── Config/
    └── config.json
```

**Information a savoir**
* **Panneau d'administration** : Tapez **`admin`** directement dans le terminal à la place d'une question pour l'IA pour accéder au panneau d'administration du programme.
* L'IA pourra vous poser des questions afin de préciser ses prochaines actions.

**Fonctionnement du programme**

* **1.** Si le dossier config existe alors le programme verifie si le fichier config.json existe dedans

* **2.** Si le fichier n'existe pas alors il vous demandera votre clé d'API Gemini qui est obligatoire pour le fonctionnement

* **3.** Ensuite le programme vous demande quoi faire

* **4.** Vous donner votre reponse puis une premier requete est envoyer a l'IA pour ouvrir un site internet

* **5.** Un scan complet de la page est effectuer, il permet de ressortir tout le text, bouton, et inpt pour le transformer en forme de texte

* **6.** Une 2ème requette est alors envoyer a l'ia avec le scan complet de la page

* **7.** L'IA renvoye alors une commande, exemple : `lien+google.com | btn_id_class+btn_valider`

* **8.** Le programme analyse la commande pour les separer en plusieurs partie a partir du '|'

* **9.** Une boucle `for` va alors regarder chaque patries de commande pour les executer

* **10.** enfin `playwright` va alors cliquer / remplir, executer les commandes

* **11.** La boucle recommence a partir du scan

```bash
git clone https://github.com/sasa747447/Projet-agent-IA.git
```
