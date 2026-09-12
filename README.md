# Projet Agent IA Autonome

Agent IA autonome piloté par l'API Gemini, s'appuyant sur l'architecture du projet "Nettoyage IA".

**Modes d'exécution**
• **Mode en ligne** : Piloté par Google Gemini pour l'analyse et l'envoi des commandes.

• **Mode local** : Propulsé par Ollama avec le modèle 'qwen2.5:7b-instruct', spécialement choisi pour sa rapidité d'exécution des commandes.

**Problématique actuelle**
Une difficulté est rencontrée avec le mode local :

Le modèle a du mal à interpréter proprement les scans HTML transmis par le script Python.

Il génère des sélecteurs fantaisistes et inadaptés.

Il ne déclenche jamais la commande question lorsqu'il est bloqué, contrairement à Gemini.

_Est-ce une limitation des capacités de raisonnement de ce modèle local par rapport à Gemini, ou un problème d'optimisation du prompt ?_

**Module python requis :**
  • msvcrt
  • json
  • shutil
  • subprocess
  • playwright
  • pathlib
  • google
  • ollama

```bash
git clone https://github.com/sasa747447/Projet-agent-IA.git
```
